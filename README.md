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

#### Driving & Configuration

##### Crawler Platform Driver (`crawler/crawler.py`)
The framework features its first integrated driver class `Crawler` implemented as an OSGAR `Node` in `crawler/crawler.py`.
- **Inputs**:
  - `desired_speed`: Receives linear and angular velocity commands (e.g. from an autonomy module).
  - `tick`: Timer inputs triggering periodic MAVLink command generation (at 10Hz).
  - `raw_serial`: Raw byte stream from the flight controller.
- **Outputs**:
  - `pose2d`: Published odometry estimates calculated from parsed feedback.
  - `rpm`: Published RPM readings from ESC telemetry.
  - `msg`: String representation of parsed MAVLink messages for diagnostics.
  - `raw_serial`: Raw MAVLink packets carrying channel override messages.

The driver parses MAVLink telemetry streams (such as `NAMED_VALUE_FLOAT` carrying `Dist_L` and `Dist_R` track travel, and `ESC_TELEMETRY_1_TO_4` carrying motor RPMs) to update and publish the robot's 2D pose and speed metrics. During each control loop iteration (triggered by `tick`), it scales the target linear and angular velocities to generate safe PWM signals, wrapping them into standard MAVLink `RC_CHANNELS_OVERRIDE` commands (Ch1 for Steering, Ch2 for Throttle, clamping outputs safely to [1100, 1900] PWM with unused channels properly set to `65535`).

##### Sample OSGAR Configuration (`config/crawler-go.json`)
A functional sample configuration is provided in `config/crawler-go.json`. This ties the platform driver together with an application module, serial transceiver, and a periodic timer:
- **`app`**: Implements the `osgar.go:Go` driver which issues simple forward-motion commands.
- **`platform`**: Uses the `crawler.crawler:Crawler` driver to manage low-level control and state feedback.
- **`serial`**: Configured to interface with the Pixhawk Cube Orange+ flight controller serial device path (e.g., `/dev/serial/by-id/usb-CubePilot...` or similar) at `115200` baud.
- **`timer`**: Emits triggers every `0.1` seconds (`10Hz`) to pace the platform controller loops.

##### Running & Verifying the Platform
To perform a platform check and record a session using the custom `uv` virtual environment:
```bash
uv run -m osgar.record config/crawler-go.json
```
This runs the OSGAR recording pipeline, binding the `Go` application logic to the `Crawler` platform driver and serial interface, and logging the raw data, inputs, and outputs.

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

#### Řízení a konfigurace

##### Ovladač platformy Crawler (`crawler/crawler.py`)
Rámec obsahuje první integrovaný ovladač platformy `Crawler` implementovaný jako OSGAR `Node` v `crawler/crawler.py`.
- **Vstupy**:
  - `desired_speed`: Přijímá příkazy pro přímočarou a úhlovou rychlost (např. z autonomního modulu).
  - `tick`: Časovač spouštějící pravidelné odesílání příkazů MAVLink (frekvence 10 Hz).
  - `raw_serial`: Surový proud dat (bajtů) ze sériového portu letového ovladače.
- **Výstupy**:
  - `pose2d`: Publikované odhady odometrie vypočítané ze zpětné vazby robota.
  - `rpm`: Publikované hodnoty RPM z telemetrie regulátorů (ESC).
  - `msg`: Textová reprezentace přijatých MAVLink zpráv pro diagnostiku.
  - `raw_serial`: Surové MAVLink pakety obsahující příkazy přepsání kanálů (RC Channel Override).

Ovladač analyzuje telemetrický proud MAVLink (např. zprávy `NAMED_VALUE_FLOAT` nesoucí ujetou vzdálenost levého/pravého pásu `Dist_L` a `Dist_R`, a zprávy `ESC_TELEMETRY_1_TO_4` s otáčkami motoru RPM), ze kterých počítá a publikuje 2D pózu a rychlost. Při každém taktu časovače (`tick`) přepočítá požadovanou dopřednou a úhlovou rychlost na bezpečné signály PWM a odešle je jako zprávy `RC_CHANNELS_OVERRIDE` protokolu MAVLink (Ch1 pro zatáčení, Ch2 pro plyn, s limity [1100, 1900] PWM a nepoužitými kanály nastavenými na hodnotu `65535`).

##### Vzorová OSGAR konfigurace (`config/crawler-go.json`)
Funkční ukázková konfigurace je uložena v souboru `config/crawler-go.json`. Propojuje ovladač platformy s aplikačním modulem, sériovým přenosem a periodickým časovačem:
- **`app`**: Využívá ovladač `osgar.go:Go`, který vydává jednoduché povely pro jízdu vpřed.
- **`platform`**: Využívá ovladač `crawler.crawler:Crawler` pro nízkoúrovňové řízení platformy.
- **`serial`**: Nakonfigurován pro komunikaci s letovým ovladačem Pixhawk Cube Orange+ na příslušné cestě k sériovému zařízení (např. `/dev/serial/by-id/usb-CubePilot...` nebo podobně) při rychlosti `115200` baud.
- **`timer`**: Generuje ticky každých `0.1` sekundy (`10 Hz`) pro periodické spouštění řídicí smyčky.

##### Spuštění a ověření platformy
Pro provedení kontroly platformy a záznamu relace s využitím virtuálního prostředí `uv` spusťte:
```bash
uv run -m osgar.record config/crawler-go.json
```
Tento příkaz spustí nahrávání OSGARu, propojí aplikační logiku `Go` s ovladačem platformy `Crawler` a sériovým rozhraním, a uloží surová i filtrovaná data do souboru protokolu (logu).
