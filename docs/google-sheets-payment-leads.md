# Сбор данных платежной формы в Google Sheets

Сайт отправляет данные из футерной формы на URL из переменной:

```bash
VITE_PAYMENT_LEADS_ENDPOINT
```

## Настройка Google Sheets

1. Откройте уже созданную Google таблицу.
2. Выберите `Extensions` -> `Apps Script`.
3. Вставьте код ниже и сохраните проект.

```js
const SHEET_NAME = "Payment Leads";

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);

  try {
    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = spreadsheet.getSheetByName(SHEET_NAME) || spreadsheet.insertSheet(SHEET_NAME);

    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        "Дата",
        "Имя",
        "Email",
        "Телефон",
        "Оферта принята",
        "Политика принята",
        "Источник",
        "Submitted at",
      ]);
    }

    const data = JSON.parse(e.postData.contents || "{}");

    sheet.appendRow([
      new Date(),
      data.name || "",
      data.email || "",
      data.phone || "",
      data.acceptedOffer === true ? "Да" : "Нет",
      data.acceptedPolicy === true ? "Да" : "Нет",
      data.source || "",
      data.submittedAt || "",
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}
```

4. Нажмите `Deploy` -> `New deployment`.
5. Тип выберите `Web app`.
6. `Execute as`: `Me`.
7. `Who has access`: `Anyone`.
8. Скопируйте URL вида `https://script.google.com/macros/s/.../exec`.

## Сборка с веб-хуком

PowerShell:

```powershell
$env:VITE_PAYMENT_LEADS_ENDPOINT="https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec"
npm.cmd run build:static
```

После сборки проверьте форму локально или на проде: заполните имя, email, телефон, поставьте оба чекбокса и нажмите `Оплатить`. В таблице должна появиться новая строка.
