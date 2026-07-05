import os
import json
import csv
import re
from datetime import datetime, timedelta

print("=== START STATISTICKÉHO ZÁPISU S VÝPOČTEM POTENCIÁLU ===")

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

# 3. Analýza makléřů a detekce obsazených krajů
obsazene_kraje = set()
pocet_makleru = 0

try:
    makleri = json.loads(surovi_makleri)
    pocet_makleru = len(makleri)
    
    # Projdeme makléře a podíváme se, jaké kraje mají zapsané
    for m in makleri:
        # Zkusíme najít klíč 'Kraj' (případně 'kraj')
        kraj_maklere = m.get("Kraj") or m.get("kraj")
        if kraj_maklere:
            obsazene_kraje.add(kraj_maklere.strip())
except Exception as e:
    print(f"Varování při analýze makléřů: {e}")

# 4. VÝPOČET POTENCIÁLU (Poměr krajů s makléři k inzerátům)
# Spočítáme inzeráty, které spadají POUZE do krajů, kde máme aspoň jednoho makléře
if pocet_inzeratu_celkem > 0 and obsazene_kraje:
    inzeraty_v_obsazenych_krajich = sum(
        1 for k in kraje_v_inzeratech if any(obsazeny in k for obsazeny in obsazene_kraje)
    )
    pomer_potencialu = (inzeraty_v_obsazenych_krajich / pocet_inzeratu_celkem) * 100
    potencial_text = f"{pomer_potencialu:.1f}%"
else:
    # Pokud nemáme data o krajích makléřů, dáme jako výchozí 100% nebo 0% podle situace
    potencial_text = "100.0%"

print(f"Fakta: Celkem inzerátů: {pocet_inzeratu_celkem}, Obsazené kraje makléři: {list(obsazene_kraje)}")
print(f"Čistý potenciál pro navolávání (obsazené kraje): {potencial_text}")

# 5. Načtení a zápis do CSV
soubor_historie = "statistika_historie.csv"
hlavicka = [
    "Datum", "Celkem_Inzeratu", "Celkem_Makleru", 
    "Inzeraty_Stredocesky", "Inzeraty_Praha", "Inzeraty_Ustecky", 
    "Inzeraty_Jihomoravsky", "Inzeraty_Moravskoslezsky",
    "Pocet_Navolanych", "Potencial_Navolavani_Procento"
]

stajici_radky = []
if os.path.exists(soubor_historie) and os.path.getsize(soubor_historie) > 0:
    try:
        with open(soubor_historie, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            lines = list(reader)
            if lines and ("Datum" in lines[0][0] or lines[0][0] == "Datum"):
                stajici_radky = lines[1:]
            else:
                stajici_radky = lines
    except Exception as e:
        print(f"Nelze přečíst starý soubor: {e}")

with open(soubor_historie, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(hlavicka)
    
    # Pokud zakládáme znovu, vložíme historické shrnutí do 3.7.[cite: 2]
    if not stajici_radky:
        # Historický základ z tvého reportu[cite: 2]
        # (Uvádíme hrubý odhad potenciálu nebo 100%, dokud se nenačtou nová denní data)
        historicky_zaklad = [
            "Do 2026-07-03", 517, 0, 103, 97, 30, 73, 70, 0, "100.0%"
        ]
        writer.writerow(historicky_zaklad)
    else:
        for row in stajici_radky:
            if row:
                writer.writerow(row)
                
    # Přidáme nový řádek s vypočítaným procentuálním základem trhu
    writer.writerow([
        datum_zprocessed, pocet_inzeratu_celkem, pocet_makleru,
        inz_stredocesky, inz_praha, inz_ustecky, 
        inz_jihomoravsky, inz_moravskoslezsky,
        0, potencial_text
    ])
    print(f"Zápis dokončen. Potenciál navolávání uložen: {potencial_text}")

print("=" * 25)
print("✅ SOUBOR AKTUALIZOVÁN")
