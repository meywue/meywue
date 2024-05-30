resolution = 64;

sides = 5;
base_radius = 70;
upper_radius_addition = 15;
base_thickness = 3;

rim_height = 20;
rim_width_base = 2;
rim_with_top = 1;

stripe_count = 5;
stripe_center_gap = 20;
stripe_diameter = 10;
stripe_radius = stripe_diameter*2/10;
stripe_z_offset = 0;
stripe_angle_offset = 18;
stripe_create_endcap = true;

module base() {
    difference() {
        cylinder(
            $fn = sides, 
            h = base_thickness + rim_height, 
            r1 = base_radius, 
            r2 = base_radius + upper_radius_addition, 
            center = false
        );
        
        translate([0, 0, base_thickness])
        cylinder(
            $fn=sides, 
            h = rim_height + 0.01,
            r1 = base_radius - rim_width_base, 
            r2 = base_radius + upper_radius_addition - rim_with_top,
            center = false
        );
    }
}

module make_ring_of(distance_from_center, count) {
    for (a = [0 : count - 1]) {
        angle = a * 360 / count + stripe_angle_offset;
        translate(distance_from_center * [sin(angle), -cos(angle), 0])
            rotate([0, 0, angle])
                children();
    }
}

// Mesh underneath the base used to reduce/remove other meshes sticking through the base
module base_remover_mesh() {
    translate([0, 0, -2 * stripe_radius + 0.01])
    cylinder(
        h = 2 * stripe_radius, 
        r1 = 2 * (base_radius+upper_radius_addition), 
        r2 = 2 * (base_radius+upper_radius_addition), 
        center = false
    );
}

module stripes() {
    // Stripes
    difference() {        
        // Instantiate stripes
        color("red")
        make_ring_of(distance_from_center = stripe_center_gap, count = stripe_count)
        translate([0, 0, base_thickness + stripe_z_offset])
        rotate([90, 0, 0])
        cylinder(
            h = base_radius, 
            r1 = stripe_radius * 2, 
            r2 = stripe_radius * 2, 
            center = false
        );
        
        // Remove lower part of the stripes so they are not leaking the saucer's base
        base_remover_mesh();
         
        // Remove all excess stripes part that are outside of the rim
        difference() {
            color("green")
            translate([0, 0, -0.01])
            cylinder(
                $fn = sides,
                h = base_thickness + rim_height, 
                r1 = 2 * (base_radius+upper_radius_addition), 
                r2 = 2 * (base_radius+upper_radius_addition), 
                center = false
            );
            
            cylinder(
                $fn = sides,
                h = base_thickness + rim_height, 
                r1 = base_radius, 
                r2 = base_radius+upper_radius_addition, 
                center = false
            );
        } 
    }
    
    if (stripe_create_endcap) {
        difference() {
            // Add spherical endcaps to stripes
            color("yellow")
            make_ring_of(distance_from_center = stripe_center_gap, count = stripe_count)
            translate([0, 0, base_thickness + stripe_z_offset])
            rotate([90, 0, 0])
            sphere(r = 2 * stripe_radius);
            
            // Remove lower part of the spheres which might be leaking the saucer's base
            base_remover_mesh();
        }
    }
}

module main() {
    $fn = resolution;
    stripes();  
    base(); 
}

main(); 