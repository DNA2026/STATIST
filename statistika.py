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

# 3. Analýza dat
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

# 4. Zápis
soubor_historie = "statistika_historie.csv"
hlavicka = ["Datum", "Celkem_Inzeratu", "Celkem_Makleru", "Inzeraty_Stredocesky", "Inzeraty_Praha", "Inzeraty_Ustecky", "Inzeraty_Jihomoravsky", "Inzeraty_Moravskoslezsky", "Pocet_Navolanych", "Potencial_Navolavani_Procento"]

stajici_radky = []
if os.path.exists(soubor_historie) and os.path.getsize(soubor_historie) > 0:
    with open(soubor_historie, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        lines = list(reader)
        if lines: stajici_radky = lines[1:]

with open(soubor_historie, mode="w", newline="\r\n", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(hlavicka)
    if not stajici_radky:
        writer.writerow(["Do 2026-07-03", 517, 0, 103, 97, 30, 73, 70, 0, "100.0%"])
    else:
        for row in stajici_radky:
            if row: writer.writerow(row)
    writer.writerow([datum_zprocessed, pocet_inzeratu_celkem, pocet_makleru, inz_stredocesky, inz_praha, inz_ustecky, inz_jihomoravsky, inz_moravskoslezsky, 0, potencial_text])
