# Crawler: Autonomous Tracked Mobile Robot Platform (Hector III - ČZU/Pro Lab)

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-OSGAR-orange.svg)](https://github.com/robotika/osgar)
[![Protocol](https://img.shields.io/badge/protocol-MAVLink-brightgreen.svg)](https://mavlink.io/en/)

This project contains the integration, drivers, and control software for the **Crawler** mobile robot platform, which corresponds to the advanced, experimental **Hecthor III** (or Hector III) Unmanned Ground Vehicle (UGV) developed by the **Technical Faculty of the Czech University of Life Sciences Prague (ČZU)** and **ProLab Engineering s.r.o.**

Tento projekt obsahuje integrační, řídicí a komunikační software pro mobilní robotickou platformu **Crawler**, která odpovídá pokročilému experimentálnímu pásovému bezosádkovému vozidlu (UGV) **Hecthor III** (či Hector III) vyvíjenému **Technickou fakultou České zemědělské univerzity v Praze (TF ČZU)** a **ProLab Engineering s.r.o.**

---

## Language / Jazyk
- [English (#english)](#english)
- [Česky (#cesky)](#cesky)

---

<a name="english"></a>
## English Description

### Overview
The **Crawler** software framework is designed to provide high-level autonomous navigation, sensor fusion, and robust communication with the physical robot platform. It builds upon two core software pillars:
1. **OSGAR** (Open Source Autonomous Rover): Handing state-machine control, 2D/3D sensor processing (LiDAR, cameras), and mission-level path planning.
2. **PyMAVLink**: Serving as the communication layer for low-level motor, steering, and throttle controls via standard MAVLink messages (e.g., overriding RC channels for differential drive control).

### The Platform: Hecthor / Hector III (ČZU / ProLab)
The Hecthor series is an state-of-the-art Czech-made multi-purpose tracked UGV platform designed to operate in extreme, hazardous, and off-road environments (including firefighting, agriculture, search & rescue, and defense).

* **Extreme Power & Drivetrain**: Powered by dual electric motors delivering up to 80 kW with extreme torque output (over 3000 Nm).
* **Compact Tracked Design**: Engineered with a low center of gravity and oscillating/trapezoidal tracks for tackling highly uneven surfaces, debris, stairs, and steep slopes.
* **Modularity**: Equipped with quick-release multi-point mounts for swapping superstructures (e.g., firefighting water monitors, rescue stretchers, agricultural sprayers, and specialized sensors).
* **Control Stack**: Utilizes a dual-tier control system where PyMAVLink relays high-level trajectory commands from OSGAR down to an onboard autopilot (e.g., Pixhawk/ArduPilot), which coordinates the raw motor controllers.

### Video Reference
To see the Czech-developed tracked robot series in action, view the demonstration video:
* **YouTube Video Link**: [Hecthor/Hector UGV Platform on YouTube](https://www.youtube.com/watch?v=UeLCBmBE9NU)

### Getting Started

#### Prerequisites
The project uses the modern Python package manager [uv](https://github.com/astral-sh/uv). Ensure you have Python 3.9+ and `uv` installed.

#### Setup & Installation
Clone the repository and install all dependencies:
```bash
uv sync
```

#### Running the Interface
To start the control interface or verification script:
```bash
uv run main.py
```

Currently, the system is configured to perform a safe connection sequence and execute a dry-run test (as captured in the debug outputs, ensuring safety by validating commands on a raised platform: *"Pásy do vzduchu!"*).

---

<a name="cesky"></a>
## Česky (Czech Description)

### Přehled
Softwarový rámec **Crawler** je navržen tak, aby poskytoval autonomní navigaci na vysoké úrovni, fúzi senzorických dat a robustní komunikaci s fyzickou robotickou platformou. Stojí na dvou hlavních softwarových pilířích:
1. **OSGAR** (Open Source Autonomous Rover): Zajišťuje řízení stavového stroje, zpracování dat z 2D/3D senzorů (LiDAR, kamery) a plánování tras na úrovni mise.
2. **PyMAVLink**: Slouží jako komunikační vrstva pro nízkoúrovňové řízení motorů, zatáčení a plynu pomocí standardních zpráv protokolu MAVLink (např. přepisování RC kanálů pro diferenciální řízení pásů).

### Robotická platforma: Hecthor / Hector III (ČZU / ProLab)
Série Hecthor je špičková, v České republice vyvíjená řada multifunkčních pásových UGV navržených pro práci v extrémních, nebezpečných a těžko prostupných podmínkách (včetně hašení požárů, zemědělství, pátracích a záchranných akcí či obrany).

* **Extrémní výkon a pohon**: Poháněno dvěma elektromotory o celkovém výkonu až 80 kW s extrémním točivým momentem (přes 3000 Nm).
* **Kompaktní pásový podvozek**: Konstruován s nízkým těžištěm a lichoběžníkovým tvarem pásů pro překonávání náročných překážek, suti, schodů a strmých svahů.
* **Modularita**: Vybaven rychloupínacími body pro snadnou výměnu nástaveb (např. hasicí lafety, evakuační nosítka, zemědělské postřikovače a mulčovače, nebo specializované senzorické hlavy).
* **Řídicí architektura**: Využívá dvouúrovňový řídicí systém, kde PyMAVLink předává povely z OSGARu do palubního autopilota (např. Pixhawk/ArduPilot), který následně řídí výkonové regulátory motorů.

### Referenční video
Chcete-li vidět tento unikátní český pásový robot v akci, můžete zhlédnout ukázkové video:
* **Odkaz na YouTube**: [Hecthor/Hector UGV platforma na YouTube](https://www.youtube.com/watch?v=UeLCBmBE9NU)

### Jak začít

#### Požadavky
Projekt využívá moderní správce Python balíčků [uv](https://github.com/astral-sh/uv). Ujistěte se, že máte nainstalovaný Python 3.9+ a nástroj `uv`.

#### Nastavení a instalace
Naklonujte repozitář a nainstalujte veškeré závislosti:
```bash
uv sync
```

#### Spuštění rozhraní
Pro spuštění komunikačního rozhraní nebo ověřovacího skriptu:
```bash
uv run main.py
```

V současné době je systém nakonfigurován tak, aby navázal bezpečné spojení s autopilotem a provedl suchý test funkčnosti (při zajištěném robotu s pásy ve vzduchu, viz log `data/output.txt`: *„Pásy do vzduchu!“*).
