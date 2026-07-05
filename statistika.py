import os
import json
import csv
import re
from datetime import datetime, timedelta

print("=== RESTART STATISTIKY – OPRAVA FORMÁTU ===")

# 1. Načtení dat z prostředí GitHub Actions
datum_raw = os.getenv("DATA_DATUM", "")
surove_inzeraty = os.getenv("DATA_INZERATY", "")
surovi_makleri = os.getenv("DATA_MAKLERI", "[]")

# Nastavení data (včerejšek)
if not datum_raw or datum_raw == "Neuvedeno":
    vypocteny_vcerejsek = datetime.now() - timedelta(days=1)
    datum_zprocessed = vypocteny_vcerejsek.strftime("%Y-%m-%d")
else:
    datum_zprocessed = datum_raw

# 2. Analýza krajů z doručeného textu inzerátů
kraje_v_inzeratech = re.findall(r"kraj\s+([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽa-záčďéěíňóřšťúůýž\s\-]+)", surove_inzeraty)
kraje_v_inzeratech = [k.strip() for k in kraje_v_inzeratech]
pocet_inzeratu_celkem = len(kraje_v_inzeratech)

# Spočítáme inzeráty pro vybrané hlavní kraje
inz_stredocesky = sum(1 for k in kraje_v_inzeratech if "Středočeský" in k)
inz_praha = sum(1 for k in kraje_v_inzeratech if "Praha" in k)
inz_ustecky = sum(1 for k in kraje_v_inzeratech if "Ústecký" in k)
inz_jihomoravsky = sum(1 for k in kraje_v_inzeratech if "Jihomoravský" in k)
inz_moravskoslezsky = sum(1 for k in kraje_v_inzeratech if "Moravskoslezský" in k)

# 3. Analýza makléřů
pocet_makleru = 0
obsazene_kraje = set()
try:
    makleri = json.loads(surovi_makleri)
    pocet_makleru = len(makleri)
    for m in makleri:
        kraj_maklere = m.get("Kraj") or m.get("kraj")
        if kraj_maklere:
            obsazene_kraje.add(kraj_maklere.strip())
except Exception as e:
    print(f"Varování při analýze makléřů: {e}")

# 4. Výpočet potenciálu
if pocet_inzeratu_celkem > 0 and obsazene_kraje:
    inzeraty_v_obsazenych_krajich = sum(
        1 for k in kraje_v_inzeratech if any(obsazeny in k for obsazeny in obsazene_kraje)
    )
    pomer_potencialu = (inzeraty_v_obsazenych_krajich / pocet_inzeratu_celkem) * 100
    potencial_text = f"{pomer_potencialu:.1f}%"
else:
    potencial_text = "100.0%"

# 5. Zápis do čistého CSV od nuly
soubor_historie = "statistika_historie.csv"
hlavicka = [
    "Datum", "Celkem_Inzeratu", "Celkem_Makleru", 
    "Inzeraty_Stredocesky", "Inzeraty_Praha", "Inzeraty_Ustecky", 
    "Inzeraty_Jihomoravsky", "Inzeraty_Moravskoslezsky",
    "Pocet_Navolanych", "Potencial_Navolavani_Procento"
]

# Jelikož jsme soubor smazali, založíme ho čistě znovu s historickým základem
with open(soubor_historie, mode="w", newline="\n", encoding="utf-8") as file:
    writer = csv.writer(file, delimiter=",")
    writer.writerow(hlavicka)
    
    # 1. řádek: Historická suma do 3.7. z tvého schváleného reportu[cite: 2]
    writer.writerow(["Do 2026-07-03", 517, 0, 103, 97, 30, 73, 70, 0, "100.0%"])
    
    # 2. řádek: Aktuálně tlačená data (za včerejšek/předchozí den)
    writer.writerow([
        datum_zprocessed, pocet_inzeratu_celkem, pocet_makleru,
        inz_stredocesky, inz_praha, inz_ustecky, 
        inz_jihomoravsky, inz_moravskoslezsky,
        0, potencial_text
    ])

print("✅ ČISTÁ STATISTIKA BYLA VYTVOŘENA A FORMÁTOVÁNA")
