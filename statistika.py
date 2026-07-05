import os
import json
import re
from datetime import datetime, timedelta

print("=== AUTOMATICKÝ ZÁPIS STATISTIKY ===")

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

# 5. Bezpečný zápis do souboru
soubor_historie = "statistika_historie.csv"

# Definujeme sloupce oddělené čárkou
hlavicka = "Datum,Celkem_Inzeratu,Celkem_Makleru,Inzeraty_Stredocesky,Inzeraty_Praha,Inzeraty_Ustecky,Inzeraty_Jihomoravsky,Inzeraty_Moravskoslezsky,Pocet_Navolanych,Potencial_Navolavani_Procento"
historicky_zaklad = "Do 2026-07-03,517,0,103,97,30,73,70,0,100.0%"
novy_radek = f"{datum_zprocessed},{pocet_inzeratu_celkem},{pocet_makleru},{inz_stredocesky},{inz_praha},{inz_ustecky},{inz_jihomoravsky},{inz_moravskoslezsky},0,{potencial_text}"

# Zkontrolujeme, zda soubor existuje a má obsah
soubor_existuje = os.path.exists(soubor_historie) and os.path.getsize(soubor_historie) > 0

if not soubor_existuje:
    # Pokud soubor neexistuje, vytvoříme ho s hlavičkou a historickým základem[cite: 2]
    with open(soubor_historie, mode="w", encoding="utf-8") as file:
        file.write(hlavicka + "\n")
        file.write(historicky_zaklad + "\n")
        file.write(novy_radek + "\n")
    print("Vytvořen nový soubor s historickým základem.")
else:
    # Pokud už soubor existuje, pouze na konec šetrně přidáme nový den
    with open(soubor_historie, mode="a", encoding="utf-8") as file:
        file.write(novy_radek + "\n")
    print(f"Přidán nový řádek pro den {datum_zprocessed}.")

print("=" * 25)
print("✅ HOTOVO")
