# Walkthrough: Direct Drive Control

Na základě schváleného plánu a doplňujících informací jsem implementoval kompletní softwarovou logiku pro Direct-Drive rover. 

Zde je shrnutí provedených změn a popis funkce nového systému.

## 1. Úprava mapování senzorů
V souboru `rpm_close_loop.lua` byly změněny indexy čtení senzorů tak, aby odpovídaly vašemu fyzickému zapojení a telemetrii z ESC:
* **Levý motor**: Index `0`
* **Pravý motor**: Index `1`

## 2. Nový Lua Script pro řízení (`direct-drive.lua`)
Celý skript byl přepsán a nyní běží na 50 Hz. Co skript dělá:
* **Sériový protokol**: Naslouchá na telemetrickém UARTu a reaguje na příkazy (`ping`, `stop`, `rpm`, `speed`, `current`). Na platný příkaz odpoví `ACK\n`, na neznámý `NACK\n` a u každého přijatého příkazu zapíše zprávu do logu letové jednotky (viditelné v konzoli Mission Planneru / Cube Manageru).
* **Uzavřená smyčka (Čistý Feedforward + Proporcionální regulace)**:
  * Z chování motorů (trace logu) jsme odvodili dokonalý fyzikální model motorů: **Mrtvá zóna = 47 PWM, Růst = 0.061 PWM / 1 RPM**.
  * Zcela jsme **odstranili integrační (I) složku**. Integrátor kvůli zpoždění odezvy RPM senzoru způsoboval nebezpečný windup (přestřely a couvání při požadavku na zpomalení). 
  * Nyní systém okamžitě přeskočí na správnou PWM hodnotu díky Feedforwardu a pouze jemně dolaďuje nepřesnosti pomocí P-regulátoru (P=0.01). Změna rychlosti je tak okamžitá a bez výkyvů.
  * Zavedli jsme pevnou ochranu směru: Regulátor nyní neumožní generovat reverzní PWM signál, pokud je požadován dopředný směr.
* **Ochrana motorů a ESC**:
  * Pokud obě kola přečtou proud vyšší než je limit nastavený přes `current` (výchozí 5 A), P-regulátor agresivně omezí PWM směrem dolů, aby proud srazil do bezpečných mezí.
* **Přepočet rychlosti**: Příkaz `speed L R` (m/s) využívá zadanou konstantu převodu 1:25 a poloměru 22 cm k automatickému dopočtu motorových RPM. 
* **Bezpečnost**: Pokud není deska Armnutá (nebo v režimu "not armed"), skript zahodí veškeré příkazy `rpm` a `speed` a vrátí chybu `NACK: Not armed`. Zároveň vnucuje motorům signál 1500 (STOP). Teprve po Armnutí začne odesílat požadovaný výkon. 

## 3. Testovací PC GUI Aplikace
Ve složce projektu přibyl nový Python skript `direct-drive-test.py` uvnitř složky `demo-direct-drive`.

* Otevře se vizuální (Tkinter) rozhraní.
* Primární ovládací rozhraní komunikuje po `COM6` (UART) s 115200 Baudy.
* Obsahuje tlačítka pro PING, STOP, nastavení proudového maxima, otáček (RPM) a lineární rychlosti (m/s).
* **Paralelní MAVLink trace log**: Kliknutím na "Start MAVLink" se aplikace na pozadí připojí k `COM5` (921600 Baud) přes `pymavlink` a asynchronně začne ukládat veškerou telemetrii (RPM, SERVO_OUTPUT_RAW) v 10Hz kvalitě do souboru `trace.log` pro zpětnou analytiku výkonu. Zprávy STATUSTEXT se tisknou i do konzole GUI.

> [!TIP]
> Pro nasazení změn nahrajte `direct-drive.lua` a `rpm_close_loop.lua` na SD kartu přes Cube Manager, a následně proveďte RESTART skriptů (nebo celé desky). Pro detailní ladění otáček spusťte `direct-drive-test.py` a nezapomeňte aktivovat MAVLink logování!
