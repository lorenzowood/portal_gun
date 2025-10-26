$fn = 100;

external_diameter = 29.631;
internal_diameter = 26.9;
nut_recess_internal_diameter = 15;
nut_recess_external_diameter = 18;
nut_recess_internal_height = 8;
nut_recess_external_height = 9;
hole_diameter = 7.2;
top_height = 1;
bottom_height = 3;
bottom_plate_thickness = 2;

knob_diameter = external_diameter;
knob_shaft_length = 9.5;
knob_shaft_diameter = 6.2;
knob_thickness_above_shaft = 2;
knob_height = knob_thickness_above_shaft + knob_shaft_length;
height_of_knob_shaft_flat_part = 1.6;

bevel_height = 20;
bevel_outer_diameter = 50;
bevel_inner_diameter = 15;
bevel_offset = 7;

translate([-25,0,0]) knob();
//translate([25,0,0]) knob_plug();
//plug_bottom_plate();

module knob() {
    difference() {
        knob_exterior();
        knob_shaft_hole();
        knob_bevel();
    }   
}

module knob_bevel() {
    translate([0,0,-bevel_offset])
    difference() {
        cylinder(h = bevel_height-2,
            d2 = bevel_outer_diameter+10,
            d1 = bevel_inner_diameter+10);
        cylinder(h = bevel_height,
            d2 = bevel_outer_diameter,
            d1 = bevel_inner_diameter);
    }
}

module knob_exterior() {
    cylinder(h = knob_height, d = knob_diameter);
}


module knob_shaft_hole() {
    knob_shaft_hole_length = knob_shaft_length + 1;
    translate([0,0,knob_thickness_above_shaft])
        difference() {
            cylinder(h = knob_shaft_hole_length, d = knob_shaft_diameter);
            translate([-external_diameter/2,height_of_knob_shaft_flat_part,0])
                cube([external_diameter, external_diameter, knob_height+1]);
        }
}

module knob_plug() {
    difference() {
        plug();
        hole();
    }
}

module plug() {
    cylinder(h=top_height, d=external_diameter);
    translate([0, 0, top_height]) cylinder(h=bottom_height, d=internal_diameter);
    cylinder(h = top_height + nut_recess_internal_height, d = nut_recess_external_diameter);
}

module hole() {
    translate([0, 0, -1])
        cylinder(h=top_height + nut_recess_external_height + 2, d=nut_recess_internal_diameter);
}

module plug_bottom_plate() {
    difference() {
        plug_bottom_plate_exterior();
        plug_bottom_plate_hole();
    }
}

module plug_bottom_plate_exterior() {
    cylinder(h = nut_recess_external_height - nut_recess_internal_height, d = nut_recess_external_diameter);
    translate([0,0,nut_recess_external_height - nut_recess_internal_height]) cylinder(h = bottom_plate_thickness, d = nut_recess_internal_diameter);
}

module plug_bottom_plate_hole() {
    translate([0,0,-1])
        cylinder(h = nut_recess_external_height + 2, d = hole_diameter);
}