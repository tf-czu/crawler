
use <vana_model.scad>
use <casmo_rear_model.scad>
use <head_model.scad>

cosmo_vyska = 584;
head_offset = 400;
naraznik_offset = -550;

// vana
VanaModel();


// pasy
for (i=[-1,1]) 
translate([i*580,0,-cosmo_vyska])
rotate([0,-90,0])
rotate([0,0,-90])
CasmoRearModel();


// head
translate([0,-head_offset,0])
HeadModel();


// narazník
color("SaddleBrown")
translate([0,naraznik_offset,-300])
cube([1480,100,60], center=true);

