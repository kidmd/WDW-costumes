// ==============================================================================
// 🏰 Main Street Electrical Parade (WDW 10K) Synchronized LED Costumes
// Parametric Fairy Light Wire Management Clips (Rigid PLA / PETG Snap-Fit)
// Resized for standard ~2.8mm to 3.05mm jacketed fairy light wires
// ==============================================================================

/* [Model Selection] */
// Which clip model to render
model_select = "all_arranged"; // [all_arranged: All 4 Arranged, 2strand_flat: 2-Strand Flat, 3strand_flat: 3-Strand Flat, 2strand_stacked: 2-Strand Stacked, 3strand_bundle: 3-Strand Triangle Bundle, test_gauge_comb: Test Gauge Comb]

// Print orientation on the build plate
print_orientation = "flat"; // [flat: Laying Flat on Base (Z=0), upright: Standing Upright (Continuous Perimeter Flex)]

/* [Wire Dimensions] */
// Measured outer diameter of single insulated fairy light wire (mm)
wire_diameter = 3.00; // [1.20:0.05:3.50]

// Radial clearance inside cavity for smooth wire glide without pinch (mm)
cavity_clearance = 0.05; // [0.00:0.01:0.20]

// Snap constriction mouth opening (mm) - smaller than wire for positive click
neck_opening = 2.20; // [1.00:0.05:2.80]

/* [Mechanical Geometry] */
// Extrusion length along wire path (mm)
clip_length = 8.00; // [5.00:0.50:20.00]

// Cantilever spring wall thickness (mm) - ~3 perimeters on 0.4mm nozzle
wall_thickness = 1.30; // [0.80:0.05:2.50]

// Bottom chassis floor thickness (mm)
floor_thickness = 1.20; // [0.80:0.05:2.50]

// Circle rendering smoothness
$fn = 48;


// ==============================================================================
// DERIVED PARAMETERS
// ==============================================================================
r_cav = wire_diameter / 2.0 + cavity_clearance;


// ==============================================================================
// 1. 2-STRAND FLAT CLIP
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
            y_neck = y_cen + 1.00;
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
// 2. 3-STRAND FLAT CLIP
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
            y_neck = y_cen + 1.00;
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
// 3. 2-STRAND STACKED VERTICAL CLIP
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
        translate([-2.25/2, y1]) square([2.25, y2 - y1]);
        
        y_neck = y2 + 1.00;
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
// 4. 3-STRAND PYRAMID BUNDLE CLIP
// ==============================================================================
module clip_3strand_bundle_2d() {
    x1 = -1.75;
    y1 = floor_thickness + r_cav;
    x2 = 1.75;
    y2 = floor_thickness + r_cav;
    x3 = 0.0;
    y3 = y1 + 2.68;
    h_total = y3 + r_cav + 0.90;
    w_bot = 2 * (1.75 + r_cav + wall_thickness);
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
        
        y_neck = y3 + 1.00;
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
    translate([0, floor_thickness + 0.30]) circle(r = 0.45);
}


// ==============================================================================
// 5. TEST GAUGE COMB (2.6, 2.8, 3.0, 3.2, 3.4 mm)
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
} else if (model_select == "test_gauge_comb") {
    render_clip_3d(ext_len = 6.0) test_gauge_comb_2d();
} else if (model_select == "all_arranged") {
    translate([-14, 0, 0]) render_clip_3d() clip_2strand_flat_2d();
    translate([14, 0, 0])  render_clip_3d() clip_3strand_flat_2d();
    translate([-14, 16, 0]) render_clip_3d() clip_2strand_stacked_2d();
    translate([14, 16, 0])  render_clip_3d() clip_3strand_bundle_2d();
    translate([0, 30, 0])   render_clip_3d(ext_len = 6.0) test_gauge_comb_2d();
}
