function odesliDataNaGitHub() {
  const MAKLERI_FILE_NAME = "Makléři.xlsx"; // Přesný název tabulky na tvém GD

  // 1. CÍLENÍ NA VČEREJŠÍ (JIŽ UZAVŘENÝ) SOUBOR INZERÁTŮ
  const cilovyDatumObj = new Date();
  cilovyDatumObj.setDate(cilovyDatumObj.getDate() - 1);
  const cilovyDatum = Utilities.formatDate(cilovyDatumObj, "GMT+2", "yyyy-MM-dd");
  const hledanyNazevInzeratu = "Inzeraty_" + cilovyDatum + ".txt";

  // Datum v názvu souboru je jednoznačné (RRRR-MM-DD), takže tu NENÍ prostor
  // pro žádné "hádání" podle data poslední úpravy nebo pořadí v iterátoru –
  // dnešní, právě se plnící soubor by totiž vždy vypadal jako "nejnovější"
  // a fallback by tak systematicky vybíral špatný (neuzavřený) soubor.
  // Pokud přesný název neexistuje, skript to nahlásí a skončí, místo aby tipoval.
  let vybranySouborInzeratu = null;

  const filesInzeraty = DriveApp.getFilesByName(hledanyNazevInzeratu);
  if (filesInzeraty.hasNext()) {
    vybranySouborInzeratu = filesInzeraty.next();

    // Pokud existuje duplicitní soubor PŘESNĚ tohoto jména (stejné datum),
    // je to samo o sobě anomálie – nahlásíme ji, ale mezi kandidáty se
    // stejným datem v názvu je bezpečné vzít ten s novější úpravou,
    // protože oba by teoreticky měli reprezentovat týž (uzavřený) den.
    if (filesInzeraty.hasNext()) {
      Logger.log("VAROVÁNÍ: nalezeno více souborů se jménem '" + hledanyNazevInzeratu + "'. Používám ten s nejnovější úpravou mezi nimi.");
      let nejnovejsi = vybranySouborInzeratu;
      while (filesInzeraty.hasNext()) {
        const kandidat = filesInzeraty.next();
        if (kandidat.getLastUpdated() > nejnovejsi.getLastUpdated()) {
          nejnovejsi = kandidat;
        }
      }
      vybranySouborInzeratu = nejnovejsi;
    }
  } else {
    // Přesný soubor pro cílové (včerejší) datum neexistuje. NEHÁDAT mezi
    // ostatními soubory "Inzeraty_*" – ty mohou být z jiných dnů, včetně
    // dnešního rozpracovaného. Radši nahlásit chybu a skončit.
    Logger.log("CHYBA: Soubor '" + hledanyNazevInzeratu + "' nebyl na Google Disku nalezen. Zpracování se přeskakuje, aby se do statistiky nedostala data ze špatného dne.");
    // Volitelně: poslat Telegram notifikaci o chybějícím souboru zde.
    return;
  }

  // Načtení obsahu textového souboru inzerátů
  const suroveInzeratyText = vybranySouborInzeratu.getBlob().getDataAsString("UTF-8");

  // Diagnostický log - kolik řádků/inzerátů soubor obsahuje, ať je hned
  // vidět v Apps Script logu, jestli sedí očekávaný počet.
  const pocetRadkuOdhad = (suroveInzeratyText.match(/\bkraj\s+\S/gi) || []).length;
  Logger.log("Použitý soubor: " + vybranySouborInzeratu.getName()
    + " | poslední úprava: " + vybranySouborInzeratu.getLastUpdated()
    + " | odhad počtu inzerátů (výskyty 'kraj'): " + pocetRadkuOdhad
    + " | délka textu: " + suroveInzeratyText.length + " znaků");

  // 2. NAČTENÍ MAKLÉŘŮ (Google Tabulka)
  const filesMakleri = DriveApp.getFilesByName(MAKLERI_FILE_NAME);
  if (!filesMakleri.hasNext()) {
    Logger.log("Soubor makléřů '" + MAKLERI_FILE_NAME + "' nebyl nalezen.");
    return;
  }
  const sheetMakleri = SpreadsheetApp.open(filesMakleri.next()).getSheets()[0];
  const dataMakleri = sheetMakleri.getDataRange().getValues();
  const jsonMakleri = tableToJson(dataMakleri);

  // 3. ODESLÁNÍ NA GITHUB
  const GITHUB_USERNAME = "DNA2026";
  const GITHUB_REPO = "STATIST";
  const GITHUB_TOKEN = PropertiesService.getScriptProperties().getProperty('ACCES_TOKEN');

  const url = "https://api.github.com/repos/" + GITHUB_USERNAME + "/" + GITHUB_REPO + "/dispatches";

  const payload = {
    "event_type": "novy_import_statistiky",
    "client_payload": {
      "datum": cilovyDatum,
      "surove_inzeraty": suroveInzeratyText,
      "makleri": jsonMakleri
    }
  };

  const options = {
    "method": "post",
    "contentType": "application/json",
    "headers": {
      "Authorization": "token " + GITHUB_TOKEN,
      "Accept": "application/vnd.github.v3+json"
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  const response = UrlFetchApp.fetch(url, options);
  Logger.log("Odezva GitHubu: " + response.getContentText());
}

// Pomocná funkce na převod tabulky makléřů do JSON objektů
function tableToJson(data) {
  if (data.length <= 1) return [];
  const headers = data[0];
  const result = [];
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    if (!row[0] || row[0].toString().trim() === "") continue; // Přeskočí prázdné řádky
    const obj = {};
    for (let j = 0; j < headers.length; j++) {
      if (row[j] instanceof Date) {
        obj[headers[j]] = Utilities.formatDate(row[j], "GMT+2", "yyyy-MM-dd");
      } else {
        obj[headers[j]] = row[j];
      }
    }
    result.push(obj);
  }
  return result;
}
