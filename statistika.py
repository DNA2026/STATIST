import os
import json
import csv
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
    datum_zpracovani = datum_raw

# 2. Výpočet základních faktů
# Spočítáme řádky (inzeráty) - vynecháme prázdné řádky
pocet_inzeratu = len([line for line in surove_inzeraty.splitlines() if line.strip()])

# Spočítáme makléře z předaného JSON pole
try:
    makleri = json.loads(surovi_makleri)
    pocet_makleru = len(makleri)
except Exception as e:
    print(f"Varování při načítání makléřů: {e}")
    pocet_makleru = 0

print(f"Fakta pro den {datum_zpracovani}: Inzerátů: {pocet_inzeratu}, Makléřů: {pocet_makleru}")

# 3. Načtení / Vytvoření historického statistického souboru
soubor_historie = "statistika_historie.csv"
hlavicka = ["Datum", "Pocet_Inzeratu", "Pocet_Makleru"]

# Zkontrolujeme, zda soubor už v repozitáři existuje
soubor_existuje = os.path.exists(soubor_historie)

# Zápis nového řádku (přidání na konec souboru - 'a')
with open(soubor_historie, mode="a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    if not soubor_existuje:
        writer.writerow(hlavicka)
        print(f"Vytvořen nový statistický soubor: {soubor_historie}")
    
    # Přidáme aktuální fakta jako nový řádek
    writer.writerow([datum_zpracovani, pocet_inzeratu, pocet_makleru])
    print(f"Nový řádek úspěšně přidán do {soubor_historie}")

print("=" * 25)
print("✅ STATISTIKA ULOŽENA")
