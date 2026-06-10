# Crawler: Autonomous Tracked Mobile Robot Platform

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-OSGAR-orange.svg)](https://github.com/robotika/osgar)
[![Protocol](https://img.shields.io/badge/protocol-MAVLink-brightgreen.svg)](https://mavlink.io/en/)

This project contains the integration, control, and communication software for the Crawler mobile robot platform, which 
is based on the chassis concept of the Hecthor experimental tracked Unmanned Ground Vehicle (UGV) developed by the 
Faculty of Engineering of the Czech University of Life Sciences Prague (TF ČZU) and ProLab Engineering s.r.o.

Tento projekt obsahuje integrační, řídicí a komunikační software pro mobilní robotickou platformu **Crawler**, která 
vychází z konceptu podvozku experimentálního pásového bezosádkového vozidla (UGV) **Hecthor** vyvíjeného 
**Technickou fakultou České zemědělské univerzity v Praze (TF ČZU)** a **ProLab Engineering s.r.o.**

---

## Language / Jazyk
- [English (#english)](#english)
- [Česky (#cesky)](#cesky)

---

<a name="english"></a>
## English Description

### Overview
The **Crawler** software framework is designed to provide high-level autonomous navigation, sensor fusion, and robust communication with the physical robot platform. It builds upon two core software pillars:
1. **OSGAR** (Open Source Garden/Generic Autonomous Robot): Handling state-machine control, 2D/3D sensor processing (LiDAR, cameras), and mission-level path planning.
2. **PyMAVLink**: Serving as the communication layer for low-level motor, steering, and throttle controls via standard MAVLink messages (e.g., overriding RC channels for differential drive control).

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

---

<a name="cesky"></a>
## Česky (Czech Description)

### Přehled
Softwarový rámec **Crawler** je navržen tak, aby poskytoval autonomní navigaci na vysoké úrovni, fúzi senzorických dat a robustní komunikaci s fyzickou robotickou platformou. Stojí na dvou hlavních softwarových pilířích:
1. **OSGAR** (Open Source Garden/Generic Autonomous Robot): Zajišťuje řízení stavového stroje, zpracování dat z 2D/3D senzorů (LiDAR, kamery) a plánování tras na úrovni mise.
2. **PyMAVLink**: Slouží jako komunikační vrstva pro nízkoúrovňové řízení motorů, zatáčení a plynu pomocí standardních zpráv protokolu MAVLink (např. přepisování RC kanálů pro diferenciální řízení pásů).

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
