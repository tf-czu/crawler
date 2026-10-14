# Hardware Specification


## Vyšší mozkové funkce

## Výzvy

- Lokalizace robota - kde je + jak je natočen 

- Traverzibilta - sjízdnost terénu, naklonění robota 

- Překážky 

### Překážky 
- Pokrytí 360° ? Minimáně, předek a boky
- Předek - Lidar , Kamera, Ultrazvuk
- Boky - Ultrazvuk? Kamery? Lidar? - slepé úhly
- Nárazník vpředu přes celou šíři robota včetně pásů
- Zadní kontrola prostoru 

#### Lidar
- 2x 

#### Radar
- Ve předu, rychlost přiblížení objeku?

#### Ultrazvuk
- nárazník vpředu (sada)
- down drop před pásy
- vzadu (sada) - kontrola zlomení / přiblížení

#### Závěs
- poloha závěsu




#### Kamery
- 360° kamera - 1x fish eye (nahoru) - pro ladění (ponětí o okolí) - co je a jaké jsou zkušenosti?
- 2x ve předu 1/4 od středu (hloubloublovou) - kontrola prostoru
- 1x kamera dozadu (hloubková)



## Komunikace

1. Ethernet PoE
2. USB Hub
3. CAN bus


## PLC 
- Siement (např Siemens 6ED1052-1CC08-0BA3 PLC řídicí modul 24 V/DC)
- STMicroelectronics Vývojová deska, STM32F767ZIT6, STM, MCU NUCLEO-F767ZI, Mikrokontrolér, ARM Cortex-M7, STM32
- nějaké alternativy ?




### Lidar 
Dva křížové paprsky pro přední část (zleva a zprava), pohled před a kolem robota
>Myšlenka, dělat věci jinak, eliminace hystorických biasů ...

Lidar 1: levý přední roh robota
Lidar 2: pravý přední roh robota
Typ: Co má Jakub v šuplíku ??? 90° Véčko (Bikónus (dvojkónus)?)

### GNSS Moduly


#### Koncept modulů
- Single - jedna anténa - Poloha (azimut za jízdy)

- Duální - dvě antény - Poloha (primární a sekundární antény) + Azimut + (azimut za jízdy) - roll nebo pitch podle orientace

- Triple - tři antény - Poloha (primární, sekundární, terciální antény) + Azimut + (azimut za jízdy) + roll + pitch


#### Eliminace False FIX:
- Loose Coupling - vylučuvání celé antény (geometrická validace polohy antén vůči sobě)
- Tight Coupling - vylučování jednotlivých signálů (MC-LAMBDA) - R/D


#### Dostupný Hardware
UM980 - Single (L1/L2/L5/L6)
UM981 - Single (L1/L2/L5/L6) + IMU
UM982 - Duální - Primární (L1/L2/L5/L6) + Sekundární (L1/L2)
> Omezení frekvencí na sekundární anténě
ZED-X20D - Duální - Primární (L1/L5/L6) + Sekundární (L1/L5/L6)
> Polohu počítá pouze z primární antény
> Nutnost naprogramovat polohu pro sekundární anténu

Ideál pro loose couplig - Duální - Primární (L1/L2/L5/L6) + Primární (L1/L2/L5/L6) + vrací polohu obou

#### Volba Modulu

Nemám tušení co vybrat ??? Každá volba nese kompromis 

Loose Coupling:
- V1 - loose coupling 2x UM982 - máme polohu 4x ikdyž 2x slabší, ale nenní nutné hledat gnss řešení z signálu satelitů

Tight Coupling: (dizertace?)
- V2 - 4x UM980, ale počítat řešení a orientaci ze signálu antén
- V2a - 2x ZED-X20D, ale počítat řešení a orientaci ze signálu antén, + méně modulů, - méně frekvencí


#### GNSS Antény 
??? Dual Four-point-feed Patch ???
Kde koupit?


#### GNSS RTK Data
Něco Jakub má ????


#### GNSS Base station?
???



## Datové služby

### GSM Modul - Internet pro RTK Data
Nějakou simku ???
> Nefunguje všude (místa bez mobilního signálu)

### GSM Modul - Internet pro RTK Data
Distribuce RTK korecí Base staion na vozidlo 
Visílač / Přijímač


## Kamery

Hloubkovou kameru? - 
Stereo kameru? - 

Co má Jakub v šuplíku ???




## Pohon

## Napájení

## Konstrukce



