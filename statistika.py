import os
import json
import csv
import re
from datetime import datetime, timedelta

# 1. Načtení dat z prostředí GitHub Actions
datum_raw = os.getenv("DATA_DATUM", "")
surove_inzeraty = os.getenv("DATA_INZERATY", "")
surovi_makleri = os.getenv("DATA_MAKLERI", "[]")

# 2. Výpočet data (vždy včerejšek)
try:
    if datum_raw and datum_raw != "Neuvedeno":
        parsed_date = datetime.strptime(datum_raw.strip(), "%Y-%m-%d")
        datum_zprocessed = (parsed_date - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        datum_zprocessed = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
except:
    datum_zprocessed = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# 3. Analýza aktuálních dat z importu
kraje_v_inzeratech = re.findall(r"kraj\s+([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽa-záčďéěíňóřšťúůýž\s\-]+)", surove_inzeraty)
kraje_v_inzeratech = [k.strip() for k in kraje_v_inzeratech]
pocet_inzeratu_celkem = len(kraje_v_inzeratech)

inz_stredocesky = sum(1 for k in kraje_v_inzeratech if "Středočeský" in k)
inz_praha = sum(1 for k in kraje_v_inzeratech if "Praha" in k)
inz_ustecky = sum(1 for k in kraje_v_inzeratech if "Ústecký" in k)
inz_jihomoravsky = sum(1 for k in kraje_v_inzeratech if "Jihomoravský" in k)
inz_moravskoslezsky = sum(1 for k in kraje_v_inzeratech if "Moravskoslezský" in k)

pocet_makleru = 0
obsazene_kraje = set()
try:
    makleri = json.loads(surovi_makleri)
    pocet_makleru = len(makleri)
    for m in makleri:
        kraj_maklere = m.get("Kraj") or m.get("kraj")
        if kraj_maklere:
            obsazene_kraje.add(kraj_maklere.strip())
except:
    pass

if pocet_inzeratu_celkem > 0 and obsazene_kraje:
    inzeraty_v_obsazenych_krajich = sum(1 for k in kraje_v_inzeratech if any(obsazeny in k for obsazeny in obsazene_kraje))
    potencial_text = f"{(inzeraty_v_obsazenych_krajich / pocet_inzeratu_celkem) * 100:.1f}%"
else:
    potencial_text = "100.0%"

# 4. Definice struktury a striktní zápis bez načítání starého souboru
soubor_historie = "statistika_historie.csv"
hlavicka = [
    "Datum", "Celkem_Inzeratu", "Celkem_Makleru", 
    "Inzeraty_Stredocesky", "Inzeraty_Praha", "Inzeraty_Ustecky", 
    "Inzeraty_Jihomoravsky", "Inzeraty_Moravskoslezsky",
    "Pocet_Navolanych", "Potencial_Navolavani_Procento", "Uspesnost_Navolavani_Procento"
]

# Vybudujeme čisté pole řádků od začátku
tabulka_dat = [
    ["2026-06-19", 120, 13, 27, 34, 0, 17, 16, 15, "70.0%", "17.9%"], # Týden 1[cite: 3]
    ["2026-06-26", 118, 13, 25, 28, 0, 22, 23, 6, "67.0%", "7.6%"],  # Týden 2[cite: 4]
    ["2026-07-03", 279, 13, 51, 35, 30, 34, 31, 16, "43.0%", "13.3%"], # Týden 3[cite: 5]
    [datum_zprocessed, pocet_inzeratu_celkem, pocet_makleru, inz_stredocesky, inz_praha, inz_ustecky, inz_jihomoravsky, inz_moravskoslezsky, 0, potencial_text, "0%"] # Nový den
]

# Zápis čistým způsobem, který GitHub Actions schválí jako Excel/CSV
with open(soubor_historie, mode="w", newline="\r\n", encoding="utf-8-sig") as file:
    writer = csv.writer(file, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(hlavicka)
    for radek in tabulka_dat:
        writer.writerow(radek)

print("=== STATISTIKA ČISTĚ PŘEPSÁNA ===")
