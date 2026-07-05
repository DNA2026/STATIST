import os
import json
import csv
import re
from datetime import datetime

print("=== START STATISTICKÉHO ZÁPISU ===")

# 1. Načtení dat z prostředí GitHub Actions
datum_raw = os.getenv("DATA_DATUM", "")
surove_inzeraty = os.getenv("DATA_INZERATY", "")
surovi_makleri = os.getenv("DATA_MAKLERI", "[]")

# Nastavení správného data zpracování
if not datum_raw or datum_raw == "Neuvedeno":
    datum_zpracovani = datetime.now().strftime("%Y-%m-%d")
else:
    datum_zpracovani = datum_raw

# 2. Analýza krajů z textu inzerátů
kraje_v_inzeratech = re.findall(r"kraj\s+([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽa-záčďéěíňóřšťúůýž\s\-]+)", surove_inzeraty)
kraje_v_inzeratech = [k.strip() for k in kraje_v_inzeratech]
pocet_inzeratu = len(kraje_v_inzeratech)

# Spočítáme inzeráty pro vybrané hlavní kraje[cite: 1, 2]
inz_stredocesky = sum(1 for k in kraje_v_inzeratech if "Středočeský" in k)
inz_praha = sum(1 for k in kraje_v_inzeratech if "Praha" in k)
inz_ustecky = sum(1 for k in kraje_v_inzeratech if "Ústecký" in k)
inz_jihomoravsky = sum(1 for k in kraje_v_inzeratech if "Jihomoravský" in k)
inz_moravskoslezsky = sum(1 for k in kraje_v_inzeratech if "Moravskoslezský" in k)

# 3. Spočítáme makléře z předaného JSON pole
try:
    makleri = json.loads(surovi_makleri)
    pocet_makleru = len(makleri)
except Exception as e:
    print(f"Varování při načítání makléřů: {e}")
    pocet_makleru = 0

print(f"Fakta pro den {datum_zpracovani}: Inzerátů celkem: {pocet_inzeratu}, Makléřů celkem: {pocet_makleru}")

# 4. Zápis do historického statistického souboru
soubor_historie = "statistika_historie.csv"

hlavicka = [
    "Datum", "Celkem_Inzeratu", "Celkem_Makleru", 
    "Inzeraty_Stredocesky", "Inzeraty_Praha", "Inzeraty_Ustecky", 
    "Inzeraty_Jihomoravsky", "Inzeraty_Moravskoslezsky",
    "Pocet_Navolanych", "Pomer_Pokryti_Kraju"
]

# Přečteme si stávající obsah, pokud existuje, abychom nepřišli o historická data
stajici_radky = []
if os.path.exists(soubor_historie):
    try:
        with open(soubor_historie, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            lines = list(reader)
            # Pokud soubor obsahuje data a první řádek je hlavička, vezmeme data pod ní
            if lines and (lines[0][0] == "Datum" or "Datum" in lines[0][0]):
                stajici_radky = lines[1:]
            else:
                stajici_radky = lines
    except Exception as e:
        print(f"Nelze přečíst starý soubor, zakládáme znovu: {e}")

# Zápis: Otevřeme v režimu 'w' (write), což soubor vyčistí a zapíše vše správně odshora dolů
with open(soubor_historie, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    # Vždy zapíšeme novou správnou hlavičku
    writer.writerow(hlavicka)
    
    # Zapíšeme zpátky stará historická data, pokud nějaká zbyla a odpovídají struktuře
    for row in stajici_radky:
        if len(row) == len(hlavicka):
            writer.writerow(row)
            
    # Přidáme nový řádek s aktuálními daty z dnešního importu
    writer.writerow([
        datum_zpracovani, pocet_inzeratu, pocet_makleru,
        inz_stredocesky, inz_praha, inz_ustecky, 
        inz_jihomoravsky, inz_moravskoslezsky,
        0, "0%"
    ])
    print(f"Data úspěšně uložena do {soubor_historie}")

print("=" * 25)
print("✅ STATISTIKA REFORMASTOVÁNA A ULOŽENA")
