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

# Pokud Google neposlal datum, použijeme aktuální dnešní datum
if not datum_raw or datum_raw == "Neuvedeno":
    datum_zpracovani = datetime.now().strftime("%Y-%m-%d")
else:
    datum_zprocessed = datum_raw

# 2. Analýza krajů z textu inzerátů
# Najdeme všechny výskyty textu "kraj XXXXX" (přehlížíme velikost písmen)
kraje_v_inzeratech = re.findall(r"kraj\s+([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽa-záčďéěíňóřšťúůýž\s\-]+)", surove_inzeraty)

# Vyčištění názvů krajů (odstranění koncové odřádkování nebo mezer)
kraje_v_inzeratech = [k.strip() for k in kraje_v_inzeratech]

# Celkový počet nalezených inzerátů na základě řádků s krajem
pocet_inzeratu = len(kraje_v_inzeratech)

# Spočítáme inzeráty pro vybrané hlavní kraje pro ukázku
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

print(f"Zpracováno pro den {datum_zpracovani}: Inzerátů celkem: {pocet_inzeratu}, Makléřůcelkem: {pocet_makleru}")

# 4. Zápis do historického statistického souboru
soubor_historie = "statistika_historie.csv"

# Rozšířená hlavička, která reflektuje byznysová fakta
hlavicka = [
    "Datum", "Celkem_Inzeratu", "Celkem_Makleru", 
    "Inzeraty_Stredocesky", "Inzeraty_Praha", "Inzeraty_Ustecky", 
    "Inzeraty_Jihomoravsky", "Inzeraty_Moravskoslezsky",
    "Pocet_Navolanych", "Pomer_Pokryti_Kraju"  # Příprava pro budoucí sloupce
]

# Zkontrolujeme, zda soubor už v repozitáři existuje a má nějaký obsah
soubor_existuje = os.path.exists(soubor_historie) and os.path.getsize(soubor_historie) > 0

# Pokud soubor neexistoval, nebo byl prázdný, přepíšeme ho s novou hlavičkou
mode = "a" if soubor_existuje else "w"

with open(soubor_historie, mode=mode, newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    if not soubor_existuje:
        writer.writerow(hlavicka)
        print(f"Vytvořen nový statistický soubor s rozšířenou hlavičkou: {soubor_historie}")
    
    # Přidáme aktuální fakta jako nový řádek (poslední dvě hodnoty necháváme zatím na 0, než dodáme tabulku navolání)
    writer.writerow([
        datum_zpracovani, pocet_inzeratu, pocet_makleru,
        inz_stredocesky, inz_praha, inz_ustecky, 
        inz_jihomoravsky, inz_moravskoslezsky,
        0, "0%"
    ])
    print(f"Nový statistický řádek úspěšně zapsán do {soubor_historie}")

print("=" * 25)
print("✅ STATISTIKA ULOŽENA")
