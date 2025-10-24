$fn = 100;

external_diameter = 29.631;
internal_diameter = 26.9;
hole_diameter = 7.2;
top_height = 1;
bottom_height = 3;


knob_diameter = external_diameter;
threaded_body_length = 8;
knob_shaft_length = 11;
knob_shaft_diameter = 6.4;
knob_thickness_above_shaft = 2;
gap_between_knob_and_plug = 1;
knob_height = knob_thickness_above_shaft + 
                knob_shaft_length +
                threaded_body_length -
                top_height -
                bottom_height -
                gap_between_knob_and_plug;
nut_recess_diameter = 20;
height_of_knob_shaft_flat_part = 1.6;

bevel_height = 20;
bevel_outer_diameter = 50;
bevel_inner_diameter = 15;
bevel_offset = 7.5;

knob();
translate([35,0,0]) knob_plug();

module knob() {
    difference() {
        knob_exterior();
        knob_nut_recess();
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

module knob_nut_recess() {

    recess_height = knob_height -
                    knob_thickness_above_shaft -
                    knob_shaft_length; 

    translate([0,0,knob_height -
                    recess_height])
        cylinder(h = recess_height + 1,
                     d = nut_recess_diameter);
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
}

module hole() {
    translate([0, 0, -1])
        cylinder(h=top_height + bottom_height + 2, d=hole_diameter);
}