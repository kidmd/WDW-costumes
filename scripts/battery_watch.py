"""Overnight webcam-based battery life monitor for WDW 10K LED costumes.

Watches a running LED costume shirt via a connected webcam, logs periodic
brightness metrics, preserves visual snapshots of the last lit frame and first
dark frame, and exits with a timestamped runtime summary once the LEDs stay off
for a sustained debounce window.
"""

from __future__ import annotations

import argparse
import csv
import ctypes
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001


@dataclass(frozen=True)
class FrameMetrics:
    """Brightness summary extracted from a single camera frame."""

    max_val: int
    p99_val: float
    bright_pixels: int
    is_on: bool


def set_keep_awake(enable: bool) -> None:
    """Prevent Windows from entering sleep while keeping display power-off allowed."""
    if sys.platform != "win32":
        return
    flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED if enable else ES_CONTINUOUS
    ctypes.windll.kernel32.SetThreadExecutionState(flags)


def parse_roi(raw: Optional[str]) -> Optional[tuple[int, int, int, int]]:
    """Parse an 'x,y,w,h' ROI string into an integer tuple."""
    if not raw:
        return None
    parts = [int(p.strip()) for p in raw.split(",")]
    if len(parts) != 4 or parts[2] <= 0 or parts[3] <= 0:
        raise ValueError(f"Invalid --roi '{raw}'. Expected 'x,y,w,h' with w,h > 0.")
    return (parts[0], parts[1], parts[2], parts[3])


def parse_start_time(raw: Optional[str], now: Optional[datetime] = None) -> Optional[datetime]:
    """Parse an ISO datetime or 'HH:MM' start time relative to `now`."""
    if not raw:
        return None
    ref = now or datetime.now()
    raw = raw.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            parsed_t = datetime.strptime(raw, fmt).time()
            candidate = datetime.combine(ref.date(), parsed_t)
            if candidate > ref:
                candidate -= timedelta(days=1)
            return candidate
        except ValueError:
            continue
    raise ValueError(f"Could not parse --start-time '{raw}'. Use 'YYYY-MM-DD HH:MM' or 'HH:MM'.")


def analyze_frame(
    frame: np.ndarray,
    brightness_threshold: int = 100,
    min_bright_pixels: int = 15,
    min_p99: float = 100.0,
    roi: Optional[tuple[int, int, int, int]] = None,
) -> FrameMetrics:
    """Compute LED-on metrics from the max-channel intensity inside the ROI."""
    region = frame
    if roi is not None:
        x, y, w, h = roi
        region = frame[y : y + h, x : x + w]

    # Use max(B, G, R) rather than grayscale luminance so saturated red/blue LEDs
    # retain full brightness signal in a dark room.
    intensity = np.max(region, axis=2) if region.ndim == 3 else region
    max_val = int(np.max(intensity))
    p99_val = float(np.percentile(intensity, 99))
    bright_pixels = int(np.count_nonzero(intensity >= brightness_threshold))
    is_on = (bright_pixels >= min_bright_pixels) or (p99_val >= min_p99)
    return FrameMetrics(
        max_val=max_val,
        p99_val=round(p99_val, 2),
        bright_pixels=bright_pixels,
        is_on=is_on,
    )


def open_camera(camera_index: int) -> cv2.VideoCapture:
    """Open webcam using DirectShow on Windows to avoid MSMF streaming stalls."""
    if sys.platform == "win32":
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if cap.isOpened():
            return cap
        cap.release()
    return cv2.VideoCapture(camera_index)


def capture_fresh_frame(cap: cv2.VideoCapture, warmup_frames: int = 3, retries: int = 5) -> np.ndarray:
    """Flush stale buffered frames and return a fresh BGR frame."""
    last_frame: Optional[np.ndarray] = None
    needed = max(1, warmup_frames)
    attempts = 0
    while attempts < needed + retries:
        attempts += 1
        ok, frame = cap.read()
        if ok and frame is not None:
            last_frame = frame
            if attempts >= needed:
                return last_frame
        else:
            time.sleep(0.25)
    if last_frame is not None:
        return last_frame
    raise RuntimeError("Failed to read frame from webcam after retries.")


class BatteryWatchStateMachine:
    """Debounced state machine tracking last-lit and confirmed-off timestamps."""

    def __init__(self, off_seconds: float) -> None:
        self.off_seconds = off_seconds
        self.last_on_time: Optional[datetime] = None
        self.last_on_frame: Optional[np.ndarray] = None
        self.first_off_time: Optional[datetime] = None
        self.first_off_frame: Optional[np.ndarray] = None
        self.confirmed_off_time: Optional[datetime] = None

    def update(self, metrics: FrameMetrics, frame: np.ndarray, ts: datetime) -> str:
        """Process one sample and return 'ON', 'DARK_PENDING', or 'CONFIRMED_OFF'."""
        if metrics.is_on:
            self.last_on_time = ts
            self.last_on_frame = frame.copy()
            self.first_off_time = None
            self.first_off_frame = None
            return "ON"

        if self.first_off_time is None:
            self.first_off_time = ts
            self.first_off_frame = frame.copy()

        elapsed_dark = (ts - self.first_off_time).total_seconds()
        if elapsed_dark >= self.off_seconds:
            self.confirmed_off_time = ts
            return "CONFIRMED_OFF"
        return "DARK_PENDING"


def format_duration(delta: timedelta) -> str:
    """Format a timedelta as 'Xh Ym Zs'."""
    total_sec = max(0, int(delta.total_seconds()))
    hours, rem = divmod(total_sec, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours}h {minutes:02d}m {seconds:02d}s"


def run_calibrate(args: argparse.Namespace) -> int:
    """Capture a calibration frame and print recommended thresholds."""
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    roi = parse_roi(args.roi)

    cap = open_camera(args.camera)
    if not cap.isOpened():
        print(f"ERROR: Could not open camera index {args.camera}.", file=sys.stderr)
        return 1
    try:
        # Let auto-exposure settle on initial open
        frame = capture_fresh_frame(cap, warmup_frames=10)
    finally:
        cap.release()

    metrics = analyze_frame(
        frame,
        brightness_threshold=args.brightness_threshold,
        min_bright_pixels=args.min_bright_pixels,
        min_p99=args.min_p99,
        roi=roi,
    )
    cal_path = out_dir / "calibration_on.png"
    cv2.imwrite(str(cal_path), frame)
    print(f"Saved calibration frame: {cal_path}")
    print(f"Frame shape: {frame.shape}")
    print(
        f"Metrics -> max_val={metrics.max_val}, p99_val={metrics.p99_val}, "
        f"bright_pixels(>={args.brightness_threshold})={metrics.bright_pixels}, is_on={metrics.is_on}"
    )
    return 0


def run_watch(args: argparse.Namespace) -> int:
    """Continuously monitor the webcam until the LEDs stay off for `off_seconds`."""
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    roi = parse_roi(args.roi)
    start_time = parse_start_time(args.start_time)

    cap = open_camera(args.camera)
    if not cap.isOpened():
        print(f"ERROR: Could not open camera index {args.camera}.", file=sys.stderr)
        return 1

    sm = BatteryWatchStateMachine(off_seconds=args.off_seconds)
    log_path = out_dir / "battery_watch_log.csv"
    watch_started = datetime.now()

    set_keep_awake(True)
    try:
        with log_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["timestamp", "max_val", "p99_val", "bright_pixels", "is_on", "state"])

            # Warm up camera auto-exposure
            _ = capture_fresh_frame(cap, warmup_frames=8)
            print(
                f"[{watch_started.strftime('%Y-%m-%d %H:%M:%S')}] Battery watch started "
                f"(interval={args.interval}s, off_debounce={args.off_seconds}s, "
                f"threshold={args.brightness_threshold}, min_pixels={args.min_bright_pixels}).",
                flush=True,
            )

            while True:
                loop_start = time.monotonic()
                now = datetime.now()
                # Read 1-2 frames to clear the single-frame UVC buffer lag
                frame = capture_fresh_frame(cap, warmup_frames=2)
                metrics = analyze_frame(
                    frame,
                    brightness_threshold=args.brightness_threshold,
                    min_bright_pixels=args.min_bright_pixels,
                    min_p99=args.min_p99,
                    roi=roi,
                )
                state = sm.update(metrics, frame, now)

                writer.writerow([
                    now.isoformat(timespec="seconds"),
                    metrics.max_val,
                    metrics.p99_val,
                    metrics.bright_pixels,
                    int(metrics.is_on),
                    state,
                ])
                csv_file.flush()

                if state == "CONFIRMED_OFF":
                    if sm.last_on_frame is not None:
                        cv2.imwrite(str(out_dir / "last_on.png"), sm.last_on_frame)
                    if sm.first_off_frame is not None:
                        cv2.imwrite(str(out_dir / "first_off.png"), sm.first_off_frame)
                    cv2.imwrite(str(out_dir / "confirmed_off.png"), frame)

                    summary = {
                        "watch_started": watch_started.isoformat(timespec="seconds"),
                        "test_start_time": start_time.isoformat(timespec="seconds") if start_time else None,
                        "last_seen_on": sm.last_on_time.isoformat(timespec="seconds") if sm.last_on_time else None,
                        "first_off_time": sm.first_off_time.isoformat(timespec="seconds") if sm.first_off_time else None,
                        "confirmed_off_time": sm.confirmed_off_time.isoformat(timespec="seconds"),
                        "total_runtime": (
                            format_duration((sm.first_off_time or sm.confirmed_off_time) - start_time)
                            if start_time
                            else None
                        ),
                    }
                    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

                    print("\n=== SHIRT BATTERY DEPLETED (CONFIRMED OFF) ===", flush=True)
                    print(json.dumps(summary, indent=2), flush=True)
                    return 0

                sleep_for = max(0.2, args.interval - (time.monotonic() - loop_start))
                time.sleep(sleep_for)
    except KeyboardInterrupt:
        print("\nBattery watch stopped by user.", flush=True)
        return 130
    finally:
        cap.release()
        set_keep_awake(False)


def run_self_test() -> int:
    """Verify brightness analysis and debounce state transitions on synthetic frames."""
    lit = np.zeros((120, 160, 3), dtype=np.uint8)
    lit[50:60, 70:90, 1] = 240  # Bright green LED cluster (200 pixels)

    dark = np.zeros((120, 160, 3), dtype=np.uint8)
    dark[:, :, :] = 8  # Dim room noise

    m_lit = analyze_frame(lit)
    m_dark = analyze_frame(dark)
    assert m_lit.is_on is True, f"Expected lit frame to be ON, got {m_lit}"
    assert m_dark.is_on is False, f"Expected dark frame to be OFF, got {m_dark}"

    sm = BatteryWatchStateMachine(off_seconds=60.0)
    t0 = datetime(2026, 11, 16, 2, 0, 0)
    assert sm.update(m_lit, lit, t0) == "ON"
    assert sm.update(m_dark, dark, t0 + timedelta(seconds=5)) == "DARK_PENDING"
    # Brief recovery resets dark streak
    assert sm.update(m_lit, lit, t0 + timedelta(seconds=10)) == "ON"
    assert sm.first_off_time is None

    # Sustained dark triggers CONFIRMED_OFF at +60s
    assert sm.update(m_dark, dark, t0 + timedelta(seconds=15)) == "DARK_PENDING"
    assert sm.update(m_dark, dark, t0 + timedelta(seconds=70)) == "DARK_PENDING"
    assert sm.update(m_dark, dark, t0 + timedelta(seconds=75)) == "CONFIRMED_OFF"
    assert sm.last_on_time == t0 + timedelta(seconds=10)
    assert sm.first_off_time == t0 + timedelta(seconds=15)
    assert parse_start_time("22:00", now=datetime(2026, 11, 15, 23, 45)) == datetime(2026, 11, 15, 22, 0)
    print("Self-test PASSED: frame metrics, debounce recovery, and shutoff timestamps verified.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Overnight webcam battery monitor for WDW LED costumes.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--calibrate", action="store_true", help="Capture one frame and print LED brightness metrics.")
    mode.add_argument("--watch", action="store_true", help="Continuously monitor until LEDs turn off.")
    mode.add_argument("--self-test", action="store_true", help="Run synthetic unit checks without opening the camera.")

    parser.add_argument("--camera", type=int, default=0, help="OpenCV camera index (default: 0).")
    parser.add_argument("--interval", type=float, default=5.0, help="Seconds between samples (default: 5.0).")
    parser.add_argument("--off-seconds", type=float, default=60.0, help="Sustained dark seconds to confirm off (default: 60).")
    parser.add_argument("--brightness-threshold", type=int, default=100, help="Pixel intensity threshold 0-255 (default: 100).")
    parser.add_argument("--min-bright-pixels", type=int, default=15, help="Min bright pixels to count as ON (default: 15).")
    parser.add_argument("--min-p99", type=float, default=100.0, help="Min 99th-percentile intensity to count as ON (default: 100).")
    parser.add_argument("--roi", type=str, default=None, help="Optional crop 'x,y,w,h'.")
    parser.add_argument("--start-time", type=str, default=None, help="Test start time ('HH:MM' or 'YYYY-MM-DD HH:MM').")
    parser.add_argument("--out-dir", type=str, default="battery_watch_output", help="Output directory for logs and snapshots.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.self_test:
        return run_self_test()
    if args.calibrate:
        return run_calibrate(args)
    return run_watch(args)


if __name__ == "__main__":
    raise SystemExit(main())
