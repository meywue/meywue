$fn = 128;

// units in cm
wall_thickness = 0.4;

lower_part_connector_is_round = true;
lower_connector_part_radius = 0.85;
lower_part_length = 10;

upper_part_connector_is_round = false;
upper_part_length = 5;
upper_connector_part_radius = 1.2;
upper_connector_part_dimension = [3,4];

add_flat_base = false;

module lower_connector_part() {
    rotate([90,0,0])
    cylinder(h = 70, r = lower_connector_part_radius, center = true);
}

module upper_connector_part() {
    translate([0, 0, lower_connector_part_radius + 2*wall_thickness + 0.5])
    cylinder(h = upper_part_length + 1, r = upper_connector_part_radius);
}

module upper_part() {
    if (upper_part_connector_is_round) {
        difference() { 
            translate([0,0,lower_connector_part_radius + wall_thickness])
            cylinder(h = upper_part_length, r = upper_connector_part_radius + wall_thickness);
            
            upper_connector_part();
        }
    }
    else {
        translate([0,0,upper_part_length/2 + 2*wall_thickness + upper_connector_part_radius/2])
        cube([upper_connector_part_dimension[0], upper_connector_part_dimension[1], upper_part_length + wall_thickness], center = true);
    }
}


module lower_part() {
    if (lower_part_connector_is_round) {
        difference() {
            //hull() {
            union() {
                // rod part
                rotate([90,0,0])
                cylinder(h = lower_part_length, r = lower_connector_part_radius + wall_thickness, center = true);
                
                // joint part
                translate([0,0,-(lower_connector_part_radius + wall_thickness)])
                cylinder(h = 2*lower_connector_part_radius + 2*wall_thickness, r = upper_connector_part_radius + wall_thickness);
                
                // flat base block
                if (add_flat_base) {
                        translate([0,0,-(lower_connector_part_radius + wall_thickness)/2])
                        cube([2*lower_connector_part_radius + 2*wall_thickness,lower_part_length, lower_connector_part_radius +               wall_thickness], center = true);
                }
            }
            lower_connector_part();
        }
    }
}

module main() {
    upper_part();
    lower_part();
}

main();


