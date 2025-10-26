$fn=50;

//cap();
//translate([0,50,0]) displaySupport();
led_bar();

module led_bar() {
    difference() {
        cube([69,17,5]);
        translate([9,9,-1]) cylinder(h=7, d=10);
        translate([34.5,9,-1]) cylinder(h=7, d=10);
        translate([60,9,-1]) cylinder(h=7, d=10);
    }
}

module cap() {
    difference() {
        union() {
            cylinder(h=2, d=36.8);
            cylinder(h=4, d=34);
        }
        translate([0,0,-1]) cylinder(h=6, d=20);
    }
}

module displaySupport() {
    translate([0,0,7]) rotate([180,0,0])difference() {
    cube([69,20,7]);
    translate([5,1.75,-1]) cube([59,16.5,4]);
    translate([55,-1,5]) cube([10,22,3]);
    }
}
