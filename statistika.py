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

# 3. Analýza všech 14 krajů z doručeného textu inzerátů
kraje_v_inzeratech = re.findall(r"kraj\s+([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽa-záčďéěíňóřšťúůýž\s\-]+)", surove_inzeraty)
kraje_v_inzeratech = [k.strip() for k in kraje_v_inzeratech]
pocet_inzeratu_celkem = len(kraje_v_inzeratech)

# Přesné mapování textu na jednotlivé kraje ČR
inz_praha = sum(1 for k in kraje_v_inzeratech if "Hlavní město Praha" in k or "Praha" in k)
inz_stredocesky = sum(1 for k in kraje_v_inzeratech if "Středočeský" in k)
inz_jihomoravsky = sum(1 for k in kraje_v_inzeratech if "Jihomoravský" in k)
inz_moravskoslezsky = sum(1 for k in kraje_v_inzeratech if "Moravskoslezský" in k)
inz_jihocesky = sum(1 for k in kraje_v_inzeratech if "Jihočeský" in k)
inz_plzensky = sum(1 for k in kraje_v_inzeratech if "Plzeňský" in k)
inz_ustecky = sum(1 for k in kraje_v_inzeratech if "Ústecký" in k)
inz_karlovarsky = sum(1 for k in kraje_v_inzeratech if "Karlovarský" in k)
inz_olomoucky = sum(1 for k in kraje_v_inzeratech if "Olomoucký" in k)
inz_vysocina = sum(1 for k in kraje_v_inzeratech if "Vysočina" in k)
inz_liberecky = sum(1 for k in kraje_v_inzeratech if "Liberecký" in k)
inz_kralovehradecky = sum(1 for k in kraje_v_inzeratech if "Královéhradecký" in k)
inz_pardubicky = sum(1 for k in kraje_v_inzeratech if "Pardubický" in k)
inz_zlinsky = sum(1 for k in kraje_v_inzeratech if "Zlínský" in k)

# 4. STATICKÁ DATA: Rozlohy krajů ČR v km²
rozlohy_kraju = {
    "Hlavní město Praha": 496,
    "Středočeský": 11015,
    "Jihomoravský": 7188,
    "Moravskoslezský": 5427,
    "Jihočeský": 10057,
    "Plzeňský": 7561,
    "Ústecký": 5335,
    "Karlovarský": 3314,
    "Olomoucký": 5272,
    "Vysočina": 6796,
    "Liberecký": 3163,
    "Královéhradecký": 4759,
    "Pardubický": 4519,
    "Zlínský": 3963
}

# Zjištění, ve kterých krajích se reálně objevil aspoň 1 inzerát
kraje_s_inzeraty = set()
if inz_praha > 0: kraje_s_inzeraty.add("Hlavní město Praha")
if inz_stredocesky > 0: kraje_s_inzeraty.add("Středočeský")
if inz_jihomoravsky > 0: kraje_s_inzeraty.add("Jihomoravský")
if inz_moravskoslezsky > 0: kraje_s_inzeraty.add("Moravskoslezský")
if inz_jihocesky > 0: kraje_s_inzeraty.add("Jihočeský")
if inz_plzensky > 0: kraje_s_inzeraty.add("Plzeňský")
if inz_ustecky > 0: kraje_s_inzeraty.add("Ústecký")
if inz_karlovarsky > 0: kraje_s_inzeraty.add("Karlovarský")
if inz_olomoucky > 0: kraje_s_inzeraty.add("Olomoucký")
if inz_vysocina > 0: kraje_s_inzeraty.add("Vysočina")
if inz_liberecky > 0: kraje_s_inzeraty.add("Liberecký")
if inz_kralovehradecky > 0: kraje_s_inzeraty.add("Královéhradecký")
if inz_pardubicky > 0: kraje_s_inzeraty.add("Pardubický")
if inz_zlinsky > 0: kraje_s_inzeraty.add("Zlínský")

# 5. Definice obsazených krajů makléři (ZGK 02)
obsazene_kraje_makleri = {"Hlavní město Praha", "Středočeský", "Jihomoravský", "Moravskoslezský", "Jihočeský", "Plzeňský"}
pocet_makleru = 9

try:
    makleri = json.loads(surovi_makleri)
    if len(makleri) > 0:
        pocet_makleru = len(makleri)
        dynamicke_kraje = set()
        for m in makleri:
            kraj_maklere = m.get("Kraj") or m.get("kraj")
            if kraj_maklere:
                # Ošetření názvu pro Prahu
                kraj_clean = kraj_maklere.strip()
                if "Praha" in kraj_clean: kraj_clean = "Hlavní město Praha"
                dynamicke_kraje.add(kraj_clean)
        if dynamicke_kraje:
            obsazene_kraje_makleri = dynamicke_kraje
except:
    pass

# 6. VÝPOČET GEOGRAFICKÉHO POTENCIÁLU PODLE ROZLOHY
rozloha_makleri_celkem = sum(rozlohy_kraju[k] for k in obsazene_kraje_makleri if k in rozlohy_kraju)
rozloha_inzeraty_celkem = sum(rozlohy_kraju[k] for k in kraje_s_inzeraty if k in rozlohy_kraju)

if rozloha_inzeraty_celkem > 0:
    geograficky_pomer = (rozloha_makleri_celkem / rozloha_inzeraty_celkem) * 100
    potencial_text = f"{geograficky_pomer:.1f}%"
else:
    potencial_text = "0.0%"

# 7. Definice široké tabulky a zápis do CSV
soubor_historie = "statistika_historie.csv"
hlavicka = [
    "Datum", "Celkem_Inzeratu", "Celkem_Makleru", 
    "Inzeraty_Praha", "Inzeraty_Stredocesky", "Inzeraty_Jihomoravsky", 
    "Inzeraty_Moravskoslezsky", "Inzeraty_Jihocesky", "Inzeraty_Plzensky", 
    "Inzeraty_Ustecky", "Inzeraty_Karlovarsky", "Inzeraty_Olomoucky", 
    "Inzeraty_Vysocina", "Inzeraty_Liberecky", "Inzeraty_Kralovehradecky", 
    "Inzeraty_Pardubicky", "Inzeraty_Zlinsky",
    "Pocet_Navolanych", "Potencial_Navolavani_Procento", "Uspesnost_Navolavani_Procento"
]

tabulka_dat = [
    ["2026-06-19", 120, 13, 34, 27, 17, 16, 14, 10, 0, 0, 1, 0, 1, 0, 0, 0, 15, "70.0%", "17.9%"], # Týden 1[cite: 3]
    ["2026-06-26", 118, 13, 28, 25, 22, 23, 9, 8, 0, 0, 3, 0, 0, 0, 0, 0, 6, "67.0%", "7.6%"],  # Týden 2
    ["2026-07-03", 279, 13, 35, 51, 34, 31, 23, 16, 30, 21, 14, 14, 3, 4, 3, 0, 16, "43.0%", "13.3%"], # Týden 3
    [
        datum_zprocessed, pocet_inzeratu_celkem, pocet_makleru,
        inz_praha, inz_stredocesky, inz_jihomoravsky, inz_moravskoslezsky,
        inz_jihocesky, inz_plzensky, inz_ustecky, inz_karlovarsky,
        inz_olomoucky, inz_vysocina, inz_liberecky, inz_kralovehradecky,
        inz_pardubicky, inz_zlinsky,
        0, potencial_text, "0%"
    ]
]

with open(soubor_historie, mode="w", newline="\r\n", encoding="utf-8-sig") as file:
    writer = csv.writer(file, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(hlavicka)
    for radek in tabulka_dat:
        writer.writerow(radek)

print(f"=== STATISTIKA ULOŽENA | GEOGRAFICKÝ POTENCIÁL: {potencial_text} ===")
