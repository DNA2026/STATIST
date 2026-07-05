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
except Exception as e:
    print(f"Chyba při parsování data '{datum_raw}': {e}")
    datum_zprocessed = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# 3. Analýza všech 14 krajů z doručeného textu inzerátů
# Přesný seznam názvů krajů místo obecného "hladového" regexu, aby se
# nespojovaly (nespolykaly) sousední inzeráty/řádky do jednoho matche.
NAZVY_KRAJU_REGEX = [
    "Hlavní město Praha", "Praha", "Středočeský", "Jihočeský", "Plzeňský",
    "Karlovarský", "Ústecký", "Liberecký", "Královéhradecký", "Pardubický",
    "Vysočina", "Jihomoravský", "Olomoucký", "Zlínský", "Moravskoslezský",
]
_pattern_kraje = r"kraj\s+(" + "|".join(re.escape(k) for k in NAZVY_KRAJU_REGEX) + r")"
kraje_v_inzeratech = re.findall(_pattern_kraje, surove_inzeraty, re.IGNORECASE)
kraje_v_inzeratech = [k.strip() for k in kraje_v_inzeratech]
pocet_inzeratu_celkem = len(kraje_v_inzeratech)

# Přesné mapování textu na jednotlivé kraje ČR
inz_praha = sum(1 for k in kraje_v_inzeratech if "Praha" in k or "Hlavní město" in k)
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

# 4. UNIKÁTNÍ MAKLÉŘI BEZ DUPLICIT
unikatni_makleri = set()
obsazene_kraje_makleri = {"Hlavní město Praha", "Středočeský", "Jihomoravský", "Moravskoslezský", "Jihočeský", "Plzeňský"}

try:
    makleri = json.loads(surovi_makleri)
    if len(makleri) > 0:
        dynamicke_kraje = set()
        for m in makleri:
            # Unikátní klíč pro osobu, aby se zamezilo duplikování lidí působících ve více krajích
            identifikace = m.get("Jméno") or m.get("jmeno") or m.get("Email") or m.get("email")
            if identifikace:
                unikatni_makleri.add(identifikace.strip())

            kraj_maklere = m.get("Kraj") or m.get("kraj")
            if kraj_maklere:
                kraj_clean = kraj_maklere.strip()
                if "Praha" in kraj_clean:
                    kraj_clean = "Hlavní město Praha"
                dynamicke_kraje.add(kraj_clean)

        if dynamicke_kraje:
            obsazene_kraje_makleri = dynamicke_kraje
except Exception as e:
    print(f"Chyba při parsování makléřů (DATA_MAKLERI): {e}")

# Žádný "magický" fallback na natvrdo zapsané číslo – pokud vstup chybí/je
# prázdný, počet je 0 a je to vidět v logu/CSV, místo aby se to tiše schovalo.
pocet_makleru_celkem = len(unikatni_makleri)
if pocet_makleru_celkem == 0:
    print("Upozornění: nebyl získán žádný unikátní makléř z DATA_MAKLERI.")

# 5. Geografické rozlohy krajů v km²
rozlohy_kraju = {
    "Hlavní město Praha": 496, "Středočeský": 11015, "Jihomoravský": 7188,
    "Moravskoslezský": 5427, "Jihočeský": 10057, "Plzeňský": 7561,
    "Ústecký": 5335, "Karlovarský": 3314, "Olomoucký": 5272,
    "Vysočina": 6796, "Liberecký": 3163, "Královéhradecký": 4759,
    "Pardubický": 4519, "Zlínský": 3963
}

kraje_s_inzeraty = set()
for kraj, hodnota in [
    ("Hlavní město Praha", inz_praha), ("Středočeský", inz_stredocesky),
    ("Jihomoravský", inz_jihomoravsky), ("Moravskoslezský", inz_moravskoslezsky),
    ("Jihočeský", inz_jihocesky), ("Plzeňský", inz_plzensky),
    ("Ústecký", inz_ustecky), ("Karlovarský", inz_karlovarsky),
    ("Olomoucký", inz_olomoucky), ("Vysočina", inz_vysocina),
    ("Liberecký", inz_liberecky), ("Královéhradecký", inz_kralovehradecky),
    ("Pardubický", inz_pardubicky), ("Zlínský", inz_zlinsky)
]:
    if hodnota > 0:
        kraje_s_inzeraty.add(kraj)

# 6. Výpočet geografického potenciálu podle rozlohy
rozloha_makleri_celkem = sum(rozlohy_kraju[k] for k in obsazene_kraje_makleri if k in rozlohy_kraju)
rozloha_inzeraty_celkem = sum(rozlohy_kraju[k] for k in kraje_s_inzeraty if k in rozlohy_kraju)

if rozloha_inzeraty_celkem > 0:
    geograficky_pomer = (rozloha_makleri_celkem / rozloha_inzeraty_celkem) * 100
    potencial_text = f"{geograficky_pomer:.1f}%"
else:
    potencial_text = "100.0%"

# 7. Zápis do CSV — APPEND, ne přepis!
# Historické řádky (19.6., 26.6., 3.7.) se použijí jen jako počáteční "seed",
# pokud soubor ještě vůbec neexistuje. Při každém dalším běhu se pouze
# přidá nový řádek na konec, historie se nikdy nesmaže.
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

seed_historie = [
    ["2026-06-19", 120, 9, 34, 27, 17, 16, 14, 10, 0, 0, 1, 0, 1, 0, 0, 0, 15, "70.0%", "17.9%"],
    ["2026-06-26", 118, 9, 28, 25, 22, 23, 9, 8, 0, 0, 3, 0, 0, 0, 0, 0, 6, "67.0%", "7.6%"],
    ["2026-07-03", 279, 9, 35, 51, 34, 31, 23, 16, 30, 21, 14, 14, 3, 4, 3, 0, 16, "43.0%", "13.3%"],
]

novy_radek = [
    datum_zprocessed, pocet_inzeratu_celkem, pocet_makleru_celkem,
    inz_praha, inz_stredocesky, inz_jihomoravsky, inz_moravskoslezsky,
    inz_jihocesky, inz_plzensky, inz_ustecky, inz_karlovarsky,
    inz_olomoucky, inz_vysocina, inz_liberecky, inz_kralovehradecky,
    inz_pardubicky, inz_zlinsky,
    0, potencial_text, "0%"
]

soubor_existuje = os.path.isfile(soubor_historie)

with open(soubor_historie, mode="a", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    if not soubor_existuje:
        writer.writerow(hlavicka)
        for radek in seed_historie:
            writer.writerow(radek)
    writer.writerow(novy_radek)

print("=== STATISTIKA ÚSPĚŠNĚ ZAPSÁNA (append) ===")
print(f"Datum: {datum_zprocessed} | Inzerátů: {pocet_inzeratu_celkem} | Makléřů: {pocet_makleru_celkem}")
