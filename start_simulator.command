#!/bin/bash
cd "$(dirname "$0")"
echo "========================================================"
echo "  Main Street Electrical Parade - LED Simulator"
echo "========================================================"
echo ""
python3 simulator.py || python simulator.py
