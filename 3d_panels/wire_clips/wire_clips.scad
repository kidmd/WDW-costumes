// ==============================================================================
// 🏰 Main Street Electrical Parade (WDW 10K) Synchronized LED Costumes
// Parametric Fairy Light Wire Management Clips & 90° Corner Elbows
// Calibrated for standard 3.20mm fairy light wiring
// ==============================================================================

/* [Model Selection] */
// Which clip or cap model to render
model_select = "all_arranged"; // [all_arranged: All Clips Arranged on Bed, all_caps_arranged: All Caps Arranged on Bed, 2strand_flat: 2-Strand Flat Clip, 3strand_flat: 3-Strand Flat Clip, 2strand_stacked: 2-Strand Stacked Clip, 3strand_bundle: 3-Strand Pyramid Clip, 2strand_pyramid_cradle: 2-Strand Pyramid Cradle, corner_90_single: 90° Single Elbow (Floating), corner_90_sewable: 90° Single Elbow (Sewable), cap_2strand_flat: Cap for 2-Strand Flat, cap_3strand_flat: Cap for 3-Strand Flat, cap_2strand_stacked: Cap for 2-Strand Stacked, cap_3strand_bundle: Cap for 3-Strand Bundle, cap_2strand_pyramid_cradle: Cap for 2-Strand Cradle, cap_corner_90: Cap for 90° Corner Elbow, test_gauge_comb: Test Gauge Comb]

// Print orientation on the build plate
print_orientation = "flat"; // [flat: Laying Flat on Base (Z=0), upright: Standing Upright (Continuous Perimeter Flex)]

/* [Wire Dimensions] */
// Measured outer diameter of single insulated fairy light wire (mm)
wire_diameter = 3.20; // [1.20:0.05:3.80]

// Radial clearance inside cavity for smooth wire glide without pinch (mm)
cavity_clearance = 0.05; // [0.00:0.01:0.20]

// Snap constriction mouth opening (mm) - smaller than wire for positive click
neck_opening = 2.35; // [1.00:0.05:3.00]

/* [Mechanical Geometry] */
// Extrusion length along wire path for straight clips (mm)
clip_length = 8.00; // [5.00:0.50:20.00]

// Cantilever spring wall thickness (mm) - ~3-4 perimeters on 0.4mm nozzle
wall_thickness = 1.35; // [0.80:0.05:2.50]

// Bottom chassis floor thickness (mm)
floor_thickness = 1.20; // [0.80:0.05:2.50]

// Circle rendering smoothness
$fn = 48;


// ==============================================================================
// DERIVED PARAMETERS
// ==============================================================================
r_cav = wire_diameter / 2.0 + cavity_clearance;


// ==============================================================================
// 1. 2-STRAND FLAT CLIP (3.2mm)
// ==============================================================================
module clip_2strand_flat_2d() {
    spacing = 2 * r_cav + wall_thickness;
    w_total = 2 * (spacing / 2.0 + r_cav + wall_thickness);
    y_cen = floor_thickness + r_cav;
    h_total = y_cen + r_cav + 0.70;

    difference() {
        hull() {
            translate([-w_total/2, 0]) square([w_total, h_total - 0.8]);
            translate([-w_total/2 + 0.8, 0]) square([w_total - 1.6, h_total]);
        }
        for (xc = [-spacing/2, spacing/2]) {
            translate([xc, y_cen]) circle(r = r_cav);
            y_neck = y_cen + 1.05;
            hw_n = neck_opening / 2.0;
            hw_t = hw_n + (h_total - y_neck) * 1.1;
            polygon([
                [xc - hw_n, y_cen],
                [xc - hw_n, y_neck],
                [xc - hw_t, h_total + 0.2],
                [xc + hw_t, h_total + 0.2],
                [xc + hw_n, y_neck],
                [xc + hw_n, y_cen]
            ]);
        }
    }
}


// ==============================================================================
// 2. 3-STRAND FLAT CLIP (3.2mm)
// ==============================================================================
module clip_3strand_flat_2d() {
    spacing = 2 * r_cav + wall_thickness;
    w_total = 2 * (spacing + r_cav + wall_thickness);
    y_cen = floor_thickness + r_cav;
    h_total = y_cen + r_cav + 0.70;

    difference() {
        hull() {
            translate([-w_total/2, 0]) square([w_total, h_total - 0.8]);
            translate([-w_total/2 + 0.8, 0]) square([w_total - 1.6, h_total]);
        }
        for (xc = [-spacing, 0, spacing]) {
            translate([xc, y_cen]) circle(r = r_cav);
            y_neck = y_cen + 1.05;
            hw_n = neck_opening / 2.0;
            hw_t = hw_n + (h_total - y_neck) * 1.1;
            polygon([
                [xc - hw_n, y_cen],
                [xc - hw_n, y_neck],
                [xc - hw_t, h_total + 0.2],
                [xc + hw_t, h_total + 0.2],
                [xc + hw_n, y_neck],
                [xc + hw_n, y_cen]
            ]);
        }
    }
}


// ==============================================================================
// 3. 2-STRAND STACKED VERTICAL CLIP (3.2mm)
// ==============================================================================
module clip_2strand_stacked_2d() {
    y1 = floor_thickness + r_cav;
    y2 = y1 + 2 * r_cav + 0.20;
    h_total = y2 + r_cav + 0.80;
    w_total = 2 * (r_cav + wall_thickness);

    difference() {
        hull() {
            translate([-w_total/2, 0]) square([w_total, h_total - 0.8]);
            translate([-w_total/2 + 0.8, 0]) square([w_total - 1.6, h_total]);
        }
        translate([0, y1]) circle(r = r_cav);
        translate([0, y2]) circle(r = r_cav);
        translate([-2.40/2, y1]) square([2.40, y2 - y1]);
        
        y_neck = y2 + 1.05;
        hw_n = neck_opening / 2.0;
        hw_t = hw_n + (h_total - y_neck) * 1.1;
        polygon([
            [-hw_n, y2],
            [-hw_n, y_neck],
            [-hw_t, h_total + 0.2],
            [hw_t, h_total + 0.2],
            [hw_n, y_neck],
            [hw_n, y2]
        ]);
    }
}


// ==============================================================================
// 4. 3-STRAND PYRAMID BUNDLE CLIP (3.2mm)
// ==============================================================================
module clip_3strand_bundle_2d() {
    x1 = -1.85;
    y1 = floor_thickness + r_cav;
    x2 = 1.85;
    y2 = floor_thickness + r_cav;
    x3 = 0.0;
    y3 = y1 + 2.85;
    h_total = y3 + r_cav + 0.90;
    w_bot = 2 * (1.85 + r_cav + wall_thickness);
    w_top = 2 * (r_cav + wall_thickness);

    difference() {
        polygon([
            [-w_bot/2, 0],
            [-w_bot/2, y1 + 0.6],
            [-w_top/2, h_total - 0.8],
            [-w_top/2 + 0.8, h_total],
            [w_top/2 - 0.8, h_total],
            [w_top/2, h_total - 0.8],
            [w_bot/2, y1 + 0.6],
            [w_bot/2, 0]
        ]);
        
        translate([x1, y1]) circle(r = r_cav);
        translate([x2, y2]) circle(r = r_cav);
        translate([x3, y3]) circle(r = r_cav);
        
        translate([-neck_opening/2, y1]) square([neck_opening, y3 - y1]);
        
        y_neck = y3 + 1.05;
        hw_n = neck_opening / 2.0;
        hw_t = hw_n + (h_total - y_neck) * 1.1;
        polygon([
            [-hw_n, y3],
            [-hw_n, y_neck],
            [-hw_t, h_total + 0.2],
            [hw_t, h_total + 0.2],
            [hw_n, y_neck],
            [hw_n, y3]
        ]);
    }
    // Center floor divider ridge
    translate([0, floor_thickness + 0.35]) circle(r = 0.50);
}


// ==============================================================================
// 5. PRESERVED 2-STRAND PYRAMID CRADLE (v1 Fit for 2 Wires)
// ==============================================================================
module clip_2strand_pyramid_cradle_2d() {
    r_v1 = 2.30 / 2 + 0.05; // 1.20mm
    fl_v1 = 1.10;
    w_v1 = 1.25;
    x1 = -1.35;
    y1 = fl_v1 + r_v1;
    x2 = 1.35;
    y2 = fl_v1 + r_v1;
    x3 = 0.0;
    y3 = y1 + 2.05;
    h_total = y3 + r_v1 + 0.80;
    w_bot = 2 * (1.35 + r_v1 + w_v1);
    w_top = 2 * (r_v1 + w_v1);

    difference() {
        polygon([
            [-w_bot/2, 0],
            [-w_bot/2, y1 + 0.5],
            [-w_top/2, h_total - 0.6],
            [-w_top/2 + 0.6, h_total],
            [w_top/2 - 0.6, h_total],
            [w_top/2, h_total - 0.6],
            [w_bot/2, y1 + 0.5],
            [w_bot/2, 0]
        ]);
        
        translate([x1, y1]) circle(r = r_v1);
        translate([x2, y2]) circle(r = r_v1);
        translate([x3, y3]) circle(r = r_v1);
        
        translate([-1.65/2, y1]) square([1.65, y3 - y1]);
        
        y_neck = y3 + 0.85;
        hw_n = 1.65 / 2.0;
        hw_t = hw_n + (h_total - y_neck) * 1.1;
        polygon([
            [-hw_n, y3],
            [-hw_n, y_neck],
            [-hw_t, h_total + 0.2],
            [hw_t, h_total + 0.2],
            [hw_n, y_neck],
            [hw_n, y3]
        ]);
    }
    translate([0, fl_v1 + 0.25]) circle(r = 0.40);
}


// ==============================================================================
// 6. 90-DEGREE CORNER ELBOW BRACKETS FOR 3-STRAND RIBBON ON EDGE
// Holds 3-strand flat fairy light ribbon oriented vertically on-edge (stacked)
// Bends across thin ~1.2mm axis (easy way) - zero copper strain or kinking!
// ==============================================================================
module vertical_ribbon_channel_radial_2d() {
    r_in = 5.0;
    slot_w = 1.65;
    slot_h = 3.60;
    floor_t = 1.20;
    wall_t = 1.40;
    neck_w = 1.00;
    lead_in_w = 2.40;
    h_total = 5.60;

    r_slot_cen = r_in + wall_t + slot_w / 2.0; // 7.225 mm
    r_out = r_in + 2 * wall_t + slot_w;        // 9.45 mm

    y_cav_top = floor_t + slot_h;              // 4.80 mm
    y_shelf = y_cav_top - 0.25;                // 4.55 mm

    difference() {
        // Outer body with chamfered top outer corners
        polygon([
            [r_in, 0],
            [r_out, 0],
            [r_out, h_total - 0.5],
            [r_out - 0.5, h_total],
            [r_in + 0.5, h_total],
            [r_in, h_total - 0.5]
        ]);
        // Cutout with distinct cantilever snap overhang lips and undercut retention shelf
        polygon([
            [r_slot_cen - lead_in_w / 2.0, h_total + 0.2],
            [r_slot_cen - neck_w / 2.0, y_cav_top],
            [r_slot_cen - slot_w / 2.0, y_shelf],
            [r_slot_cen - slot_w / 2.0, floor_t],
            [r_slot_cen + slot_w / 2.0, floor_t],
            [r_slot_cen + slot_w / 2.0, y_shelf],
            [r_slot_cen + neck_w / 2.0, y_cav_top],
            [r_slot_cen + lead_in_w / 2.0, h_total + 0.2]
        ]);
    }
}

module clip_corner_90_single_3d() {
    // Pure 90-degree curved sweep - 3-strand ribbon on edge with cantilever snap lips
    rotate_extrude(angle = 90)
        vertical_ribbon_channel_radial_2d();
}

module clip_corner_90_sewable_3d() {
    clip_corner_90_single_3d();
    // 2 outer corner sewing eyelet tabs placed completely outside the 9.45mm channel wall
    // Center at (11.2, 2.0) and (2.0, 11.2) gives 100% clear 2.0mm holes with solid base root overlap into channel base
    difference() {
        union() {
            translate([11.2, 2.0, 0]) cylinder(h = 1.2, r = 2.5);
            translate([2.0, 11.2, 0]) cylinder(h = 1.2, r = 2.5);
        }
        translate([11.2, 2.0, -0.1]) cylinder(h = 1.4, r = 1.0);
        translate([2.0, 11.2, -0.1]) cylinder(h = 1.4, r = 1.0);
    }
}


// ==============================================================================
// 7. TEST GAUGE COMB (2.6, 2.8, 3.0, 3.2, 3.4 mm)
// ==============================================================================
module test_gauge_comb_2d() {
    diameters = [2.6, 2.8, 3.0, 3.2, 3.4];
    slot_spacing = 7.0;
    w_total = (len(diameters) - 1) * slot_spacing + 2 * (1.75 + 1.30) + 2.0;
    h_total = 5.3;
    floor = 1.2;

    difference() {
        translate([-w_total/2, 0]) square([w_total, h_total]);
        for (i = [0:len(diameters)-1]) {
            d = diameters[i];
            xc = - (len(diameters) - 1) * slot_spacing / 2.0 + i * slot_spacing;
            rc = d / 2.0 + 0.05;
            nw = d * 0.73;
            yc = floor + rc;
            translate([xc, yc]) circle(r = rc);
            yn = yc + (d * 0.32);
            hwn = nw / 2.0;
            hwt = hwn + (h_total - yn) * 1.1;
            polygon([
                [xc - hwn, yc], [xc - hwn, yn], [xc - hwt, h_total + 0.2],
                [xc + hwt, h_total + 0.2], [xc + hwn, yn], [xc + hwn, yc]
            ]);
        }
    }
}


// ==============================================================================
// 8. SNAP-ON RACE-DAY SECURITY CAPS (ROOFS)
// Positive-locking armored hoods that snap over clips to lock wires down for 10K
// ==============================================================================
module straight_cap_2d(clip_top_w, clip_h, skirt_depth = 2.20) {
    tolerance = 0.12;
    roof_t = 1.00;
    leg_t = 1.10;
    bead_depth = 0.35;
    bead_h = 0.60;
    
    inner_w = clip_top_w + 2 * tolerance;
    outer_w = inner_w + 2 * leg_t;
    y_clip_top = clip_h;
    y_cap_top = y_clip_top + roof_t;
    y_leg_bot = y_clip_top - skirt_depth;
    y_bead = y_clip_top - 1.20;
    
    difference() {
        hull() {
            translate([-outer_w/2, y_leg_bot]) square([outer_w, y_cap_top - y_leg_bot - 0.5]);
            translate([-outer_w/2 + 0.5, y_leg_bot]) square([outer_w - 1.0, y_cap_top - y_leg_bot]);
        }
        polygon([
            [-inner_w/2 + bead_depth, y_leg_bot - 0.1],
            [-inner_w/2 + bead_depth, y_bead - bead_h/2],
            [-inner_w/2, y_bead],
            [-inner_w/2, y_clip_top + 0.1],
            [inner_w/2, y_clip_top + 0.1],
            [inner_w/2, y_bead],
            [inner_w/2 - bead_depth, y_bead - bead_h/2],
            [inner_w/2 - bead_depth, y_leg_bot - 0.1]
        ]);
    }
}

module render_cap_3d(clip_top_w, clip_h, ext_len = clip_length) {
    // Rotated so flat roof sits flat at Z=0 and legs point UP (+Z)
    rotate([-90, 0, 0])
        translate([0, - (clip_h + 1.00), 0])
            linear_extrude(height = ext_len)
                straight_cap_2d(clip_top_w, clip_h);
}

module cap_corner_90_3d() {
    r_in = 5.00;
    r_out = 9.45;
    h_clip = 5.60;
    tolerance = 0.12;
    roof_t = 1.00;
    leg_t = 1.10;
    bead_depth = 0.35;
    bead_h = 0.60;
    
    r_cap_in = r_in - tolerance - leg_t;
    r_cap_out = r_out + tolerance + leg_t;
    y_cap_top = h_clip + roof_t;
    y_bead = h_clip - 1.20;
    y_leg_bot = y_bead - bead_h/2.0 - 0.30;
    
    r_clip_inner_face = r_in - tolerance;
    r_clip_outer_face = r_out + tolerance;

    rotate([180, 0, 0])
        translate([0, 0, -y_cap_top])
            rotate_extrude(angle = 90) {
                difference() {
                    hull() {
                        translate([r_cap_in, y_leg_bot]) square([r_cap_out - r_cap_in, y_cap_top - y_leg_bot - 0.5]);
                        translate([r_cap_in + 0.5, y_leg_bot]) square([r_cap_out - r_cap_in - 1.0, y_cap_top - y_leg_bot]);
                    }
                    polygon([
                        [r_clip_inner_face - bead_depth, y_leg_bot - 0.1],
                        [r_clip_inner_face - bead_depth, y_bead - bead_h/2.0],
                        [r_clip_inner_face, y_bead],
                        [r_clip_inner_face, h_clip + 0.1],
                        [r_clip_outer_face, h_clip + 0.1],
                        [r_clip_outer_face, y_bead],
                        [r_clip_outer_face + bead_depth, y_bead - bead_h/2.0],
                        [r_clip_outer_face + bead_depth, y_leg_bot - 0.1]
                    ]);
                }
            }
}


// ==============================================================================
// 3D EXTRUSION & ORIENTATION HELPER
// ==============================================================================
module render_clip_3d(ext_len = clip_length) {
    if (print_orientation == "flat") {
        rotate([90, 0, 0])
            linear_extrude(height = ext_len)
                children();
    } else {
        linear_extrude(height = ext_len)
            children();
    }
}


// ==============================================================================
// MAIN ASSEMBLY SELECTOR
// ==============================================================================
if (model_select == "2strand_flat") {
    render_clip_3d() clip_2strand_flat_2d();
} else if (model_select == "3strand_flat") {
    render_clip_3d() clip_3strand_flat_2d();
} else if (model_select == "2strand_stacked") {
    render_clip_3d() clip_2strand_stacked_2d();
} else if (model_select == "3strand_bundle") {
    render_clip_3d() clip_3strand_bundle_2d();
} else if (model_select == "2strand_pyramid_cradle") {
    render_clip_3d() clip_2strand_pyramid_cradle_2d();
} else if (model_select == "corner_90_single") {
    clip_corner_90_single_3d();
} else if (model_select == "corner_90_sewable") {
    clip_corner_90_sewable_3d();
} else if (model_select == "cap_2strand_flat") {
    render_cap_3d(10.65, 5.01);
} else if (model_select == "cap_3strand_flat") {
    render_cap_3d(15.30, 5.01);
} else if (model_select == "cap_2strand_stacked") {
    render_cap_3d(6.00, 8.55);
} else if (model_select == "cap_3strand_bundle") {
    render_cap_3d(6.00, 7.93);
} else if (model_select == "cap_2strand_pyramid_cradle") {
    render_cap_3d(4.90, 6.27);
} else if (model_select == "cap_corner_90") {
    cap_corner_90_3d();
} else if (model_select == "test_gauge_comb") {
    render_clip_3d(ext_len = 6.0) test_gauge_comb_2d();
} else if (model_select == "all_caps_arranged") {
    translate([-15, 0, 0])  render_cap_3d(10.65, 5.01);
    translate([15, 0, 0])   render_cap_3d(15.30, 5.01);
    translate([-15, 16, 0]) render_cap_3d(6.00, 8.55);
    translate([15, 16, 0])  render_cap_3d(6.00, 7.93);
    translate([0, 32, 0])   render_cap_3d(4.90, 6.27);
    translate([0, 48, 0])   cap_corner_90_3d();
} else if (model_select == "all_arranged") {
    translate([-15, 0, 0]) render_clip_3d() clip_2strand_flat_2d();
    translate([15, 0, 0])  render_clip_3d() clip_3strand_flat_2d();
    translate([-15, 16, 0]) render_clip_3d() clip_2strand_stacked_2d();
    translate([15, 16, 0])  render_clip_3d() clip_3strand_bundle_2d();
    translate([0, 32, 0])   render_clip_3d() clip_2strand_pyramid_cradle_2d();
    translate([-18, 48, 0]) clip_corner_90_single_3d();
    translate([18, 48, 0])  clip_corner_90_sewable_3d();
    translate([0, 68, 0])   render_clip_3d(ext_len = 6.0) test_gauge_comb_2d();
}
