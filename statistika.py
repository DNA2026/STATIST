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
inz_liberecký = sum(1 for k in kraje_v_inzeratech if "Liberecký" in k)
inz_kralovehradecky = sum(1 for k in kraje_v_inzeratech if "Královéhradecký" in k)
inz_pardubicky = sum(1 for k in kraje_v_inzeratech if "Pardubický" in k)
inz_zlinsky = sum(1 for k in kraje_v_inzeratech if "Zlínský" in k)

# 4. Analýza makléřů a obsazených krajů
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

# 5. Výpočet potenciálu pro navolávání
if pocet_inzeratu_celkem > 0 and obsazene_kraje:
    inzeraty_v_obsazenych_krajich = sum(1 for k in kraje_v_inzeratech if any(obsazeny in k for obsazeny in obsazene_kraje))
    potencial_text = f"{(inzeraty_v_obsazenych_krajich / pocet_inzeratu_celkem) * 100:.1f}%"
else:
    potencial_text = "100.0%"

# 6. Definice kompletní široké tabulky (všech 14 krajů)
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

# Rekonstrukce kompletní historie týdnů přesně podle tvých HTML reportů
tabulka_dat = [
    # Týden 1 (15.06. - 19.06. 2026) -> Celkem 120 zakázek
    ["2026-06-19", 120, 13, 34, 27, 17, 16, 14, 10, 0, 0, 1, 0, 1, 0, 0, 0, 15, "70.0%", "17.9%"],
    # Týden 2 (22.06. - 26.06. 2026) -> Celkem 118 zakázek
    ["2026-06-26", 118, 13, 28, 25, 22, 23, 9, 8, 0, 0, 3, 0, 0, 0, 0, 0, 6, "67.0%", "7.6%"],
    # Týden 3 (27.06. - 03.07. 2026) -> Celkem 279 zakázek
    ["2026-07-03", 279, 13, 35, 51, 34, 31, 23, 16, 30, 21, 14, 14, 3, 4, 3, 0, 16, "43.0%", "13.3%"],
    # Nový den (4.7.) doručený z Google tabulky
    [
        datum_zprocessed, pocet_inzeratu_celkem, pocet_makleru,
        inz_praha, inz_stredocesky, inz_jihomoravsky, inz_moravskoslezsky,
        inz_jihocesky, inz_plzensky, inz_ustecky, inz_karlovarsky,
        inz_olomoucky, inz_vysocina, inz_liberecký, inz_kralovehradecky,
        inz_pardubicky, inz_zlinsky,
        0, potencial_text, "0%"
    ]
]

# Striktní a čistý zápis kompletní matice
with open(soubor_historie, mode="w", newline="\r\n", encoding="utf-8-sig") as file:
    writer = csv.writer(file, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(hlavicka)
    for radek in tabulka_dat:
        writer.writerow(radek)

print("=== DEFENITIVNÍ HISTORIE VŠECH KRAJŮ ZAPSÁNA ===")
