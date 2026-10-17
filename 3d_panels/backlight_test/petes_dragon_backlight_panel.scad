// ============================================================================
// 🏰 Main Street Electrical Parade - Pete's Dragon Backlighting Test Panel
// Flat 200mm x 200mm Square Panel | Centered 180mm Dragon
// All colors extend full Z thickness
// ============================================================================

// SELECT THICKNESS HERE (Default: 0.80 mm)
panel_thickness = 0.80; // Options: 1.00, 0.80, 0.60, 0.48

chassis_size = 200.0;
dragon_w = 180.00;
dragon_h = 163.24;
offset_x = 10.00;
offset_y = 18.38;

// Renders the solid monolithic block or imports color STLs
module backlight_panel(t = panel_thickness) {
    cube([chassis_size, chassis_size, t], center = false);
}

backlight_panel(panel_thickness);
