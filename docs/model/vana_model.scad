


vana_vyska = 300;

vana_sirka = 685;
vana_delka = 1100;

vana_offset = 450;

VanaModel();

module VanaModel(){

    color("white")
    translate([-vana_sirka/2,-vana_offset,-vana_vyska])
    difference() {
        cube([vana_sirka,vana_delka,vana_vyska]);
        //translate([5,5,5])
        //cube([vana_sirka-10,vana_delka-10,vana_vyska]);
    }

}

