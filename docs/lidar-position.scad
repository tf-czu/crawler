

module lidar() {

cylinder(h =100, d1=0, d=200);

mirror([0,0,1])
cylinder(h =100, d1=0, d=200);

}


cube([1000,1500,200]);


translate([0,0,200])
rotate([30,-45,0])
lidar();



translate([1000,0,0])
mirror([1,0,0])
translate([0,0,200])
rotate([30,-45,0])
lidar();