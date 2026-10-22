// CAMSO X4S - REAR
// https://powersports.camso.co/en-ca/atv-utv/track-systems/x4s


/*
Drive type
Internal drive
Sprocket
15 to 18 teeth
Frame
Carbon steel
Anti-rotation
Redesigned mild steel anti-rotation single rate spring and progressive damper.
Quick connect steering limiter design.
Weight
F: 32.7 kg
R: 35.8 kg
Mount kit: 2.72 kg (approx.)
Hub & bearings
Cast steel multi-bolt (4) pattern
Wheels & bearings
134 & 202 mm double bearing wheels. Standard and replaceable sealed bearings. Elastomer outer band. Bladder-type wheel cap.
Rubber track design
F: Flex
R: Flat
Track length
F: 236.2 cm
R: 248.9 cm
Track lug height
F: 2.54 cm
R: 2.54 cm
Track width
F: 27.9 cm
R: 30.5 cm


System length
F: 101.6 cm
R: 106.7 cm

Offset length
F: 61 cm
R: 68.6 cm

System width
F: 27.9 cm
R: 30.5 cm

Offset width
15.2 cm

Ground clearance
F: 39 cm
R: 37.1 cm

System height
F: 58.4 cm
R: 58.4 cm
*/


pas_sirka = 1067; // mm

pas_offset = 686; // mm

pas_width = 305; // mm

pas_osa_nad_zemi = 371; 

pas_vyska = 584; // mm

idlerWheelRadius = 100;
mainWheelRadius = 203;
supportWheelRadius = 65;

CasmoRearModel();

module CasmoRearModel() {

    color("gray") {
    
        WheelsPosition();

        for (i=[1:4]) {
            translate([-pas_offset+pas_sirka/7*i+supportWheelRadius*2+20,supportWheelRadius,0])
            SupportWheel();

        }


        Pas();

    }

}



module Pas() {

linear_extrude(height = pas_width, convexity = 10, center = true) 
difference() {
    CasmoRearShape();
    offset(r = -30)
    CasmoRearShape();
    
}

}


module CasmoRearShape() {
    hull()
    projection(cut = true)
    WheelsPosition();

}


module WheelsPosition() {

translate([0,pas_osa_nad_zemi,0])
MainWheel();


translate([-(pas_offset-idlerWheelRadius),idlerWheelRadius,0])
IdlerWheel();

translate([(pas_sirka-pas_offset)-idlerWheelRadius,idlerWheelRadius,0])
IdlerWheel();

}

module MainWheel() {

    cylinder(r=mainWheelRadius, h=100, center=true);

}

module IdlerWheel() {

    cylinder(r=idlerWheelRadius, h=80, center=true);

}

module SupportWheel() {

    cylinder(r=supportWheelRadius, h=80, center=true);

}