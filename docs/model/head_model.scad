
head_vyska = 250;



HeadModel();

module HeadModel() {

translate([-300,0,0]) {

    // bedna
    color("white")
    cube([600,600,head_vyska]);


    //lidar A
    translate([-30,-30,head_vyska+30])
    rotate([33,-45,0])
    lidar();


    //lidar B
    translate([600,0,0])
    mirror([1,0,0])
    translate([-30,-30,head_vyska+30])
    rotate([33,-45,0])
    lidar();


    //gnss anténa 1
    translate([300,50, head_vyska])
    GnssAntena();

    //gnss anténa 2
    translate([300,600-50, head_vyska])
    GnssAntena();

    //gnss anténa 3
    translate([600-50, 300, head_vyska])
    GnssAntena();

    //gnss anténa 4
    translate([50,300, head_vyska])
    GnssAntena();


    //kamera přední
    translate([300,0,head_vyska-70])
    camera();


    //kamera zadní
    translate([300,600,head_vyska-70])
    camera();


}

}




module GnssAntena() {
    
    // 456-33-VSP6037L-58
color("lightgreen") {
    translate([0, 0, -100+50]) 
    difference() {
        sphere(r=100);
        translate([-100,-100,-100-43.4])
        cube([200,200,200]);
        
    }
}


}


module lidar() {

color("orange") {
   
    cylinder(h =50, d1=0, d2=100);
    mirror([0,0,1])
    cylinder(h =50, d1=0, d2=100);
}

}



module camera() {

color("DodgerBlue") {

    cube([250,50,50], center=true);
}


}
