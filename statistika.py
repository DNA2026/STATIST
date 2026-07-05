import os
import json

print("=== START PYTHON ANALÝZY ===")

# 1. Načtení dat z prostředí GitHub Actions
datum = os.getenv("DATA_DATUM", "Neuvedeno")
surove_inzeraty = os.getenv("DATA_INZERATY", "Žádná data")
surovi_makleri = os.getenv("DATA_MAKLERI", "[]")

print(f"Zpracovávám data pro datum: {datum}")
print("-" * 40)

# 2. Výpis inzerátů
print("DORUČENÉ INZERÁTY:")
print(surove_inzeraty)
print("-" * 40)

# 3. Načtení a výpis makléřů
print("DORUČENÍ MAKLÉŘI:")
try:
    makleri = json.loads(surovi_makleri)
    print(f"Úspěšně načteno {len(makleri)} makléřů.")
    for m in makleri:
        # Vypíšeme jméno makléře (předpokládáme sloupec 'Jméno' nebo první klíč)
        jmeno = m.get("Jméno") or m.get("jmeno") or list(m.values())[0]
        print(f"-> Makléř: {jmeno}")
except Exception as e:
    print(f"Chyba při parsování makléřů: {e}")

print("=" * 25)
print("✅ ANALÝZA ÚSPĚŠNĚ DOKONČENA")
