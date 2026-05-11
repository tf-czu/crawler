# Záznam z první instalace a konfigurace robota

## 1. Systémové informace
* [cite_start]**Operační systém:** Ubuntu 26.04 LTS (GNU/Linux 7.0.0-15-generic x86_64)[cite: 4].
* [cite_start]**Připojení:** SSH spojení bylo navázáno na adresu 192.168.1.109 pod uživatelským jménem robot[cite: 1, 4].
* [cite_start]**Stav po přihlášení:** Systém byl aktuální s nízkou zátěží a teplota procesoru byla 56,9 °C[cite: 4]. [cite_start]Bylo využito 0 % kapacity disku /home a 2 % operační paměti[cite: 4].

## 2. Provedené aktualizace a instalace
* [cite_start]Byly vyhledány a staženy aktuální verze systémových balíčků[cite: 7].
* [cite_start]Proběhl úspěšný upgrade balíčku distro-info-data[cite: 9, 10].
* [cite_start]V systému jsou přítomny a ručně označeny základní nástroje htop, screen, vim, git a curl[cite: 13, 14, 15, 16].
* [cite_start]Byl úspěšně nainstalován textový správce souborů mc (Midnight Commander) a jeho závislosti[cite: 18, 34].
* [cite_start]Nástroj pro správu Python prostředí uv byl stažen a nainstalován ve verzi 0.11.13[cite: 38].

## 3. Adresářová struktura a Git
* [cite_start]Byly vytvořeny složky pro logy a projekty v domovském adresáři[cite: 39].
* [cite_start]Ve složce ~/git/bare/ byly inicializovány bare repozitáře osgar.git a crawler.git[cite: 39, 42, 45].
* [cite_start]Tyto repozitáře byly naklonovány do produkčních složek ~/git/osgar a ~/git/crawler[cite: 39, 46].
* [cite_start]Do souboru .bashrc byly přidány cesty pro PYTHONPATH a OSGAR_LOGS a prostředí bylo následně načteno[cite: 47].

## 4. Hardware, Disky a Síť (Autoinstall konfigurace)
* [cite_start]**Úložiště:** Hlavním diskem je NVMe modul Samsung SSD 980 s kapacitou 1TB[cite: 52].
* [cite_start]Oddíl pro zavaděč systému má formát fat32 a je připojen do bodu /boot/efi[cite: 53, 54, 56].
* [cite_start]Systémový kořenový oddíl (/) o velikosti zhruba 100 GB využívá souborový systém ext4[cite: 54, 55].
* [cite_start]Datový oddíl využívá zbytek dostupné kapacity disku, má formát ext4 a je připojen do /home[cite: 55, 56].
* [cite_start]**Síťová konfigurace:** Rozhraní enp2s0 má nastavenou podporu DHCP pro IPv4 a IPv6 adresy[cite: 51].