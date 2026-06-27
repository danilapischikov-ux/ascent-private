import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";

const projectRoot = process.cwd();
const sourcePath = path.join(projectRoot, "src", "components", "site", "Faq.tsx");
const outputDir = path.join(projectRoot, "exports");
const outputPath = path.join(outputDir, "FAQ_Ascent_Private.xlsx");

const source = fs.readFileSync(sourcePath, "utf8");

const faqBlock = source.match(/const faqs = \[([\s\S]*?)\];\s*\n\s*const faqCategories/);
const categoryBlock = source.match(/const faqCategories = \[([\s\S]*?)\];\s*\n\s*export function/);

if (!faqBlock || !categoryBlock) {
  throw new Error("Could not find FAQ data in Faq.tsx");
}

const decodeString = (value) => JSON.parse(`"${value}"`);

const faqs = [
  ...faqBlock[1].matchAll(/\{\s*q:\s*"((?:\\.|[^"\\])*)",\s*a:\s*"((?:\\.|[^"\\])*)",\s*\}/g),
].map((match, index) => ({
  number: index + 1,
  question: decodeString(match[1]),
  answer: decodeString(match[2]),
}));

const categoryByQuestion = new Map();

for (const match of categoryBlock[1].matchAll(
  /\{\s*title:\s*"((?:\\.|[^"\\])*)",\s*questionNumbers:\s*\[([^\]]+)\],\s*\}/g,
)) {
  const title = decodeString(match[1]);
  const numbers = match[2]
    .split(",")
    .map((value) => Number(value.trim()))
    .filter(Boolean);

  for (const number of numbers) {
    categoryByQuestion.set(number, title);
  }
}

const rows = [
  ["№", "Категория", "Вопрос", "Ответ"],
  ...faqs.map((item) => [
    String(item.number),
    categoryByQuestion.get(item.number) || "",
    item.question,
    item.answer,
  ]),
];

const escapeXml = (value) =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");

const columnName = (index) => {
  let name = "";
  let current = index + 1;

  while (current > 0) {
    const remainder = (current - 1) % 26;
    name = String.fromCharCode(65 + remainder) + name;
    current = Math.floor((current - 1) / 26);
  }

  return name;
};

const sheetData = rows
  .map((row, rowIndex) => {
    const cells = row
      .map((cell, cellIndex) => {
        const address = `${columnName(cellIndex)}${rowIndex + 1}`;
        const style = rowIndex === 0 ? 1 : 2;

        return `<c r="${address}" s="${style}" t="inlineStr"><is><t xml:space="preserve">${escapeXml(cell)}</t></is></c>`;
      })
      .join("");

    return `<row r="${rowIndex + 1}">${cells}</row>`;
  })
  .join("");

const files = new Map([
  [
    "[Content_Types].xml",
    `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>`,
  ],
  [
    "_rels/.rels",
    `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>`,
  ],
  [
    "docProps/core.xml",
    `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>FAQ Ascent Private</dc:title>
  <dc:creator>Ascent Private</dc:creator>
  <cp:lastModifiedBy>Ascent Private</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">${new Date().toISOString()}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">${new Date().toISOString()}</dcterms:modified>
</cp:coreProperties>`,
  ],
  [
    "docProps/app.xml",
    `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Ascent Private Export</Application>
</Properties>`,
  ],
  [
    "xl/workbook.xml",
    `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="FAQ" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>`,
  ],
  [
    "xl/_rels/workbook.xml.rels",
    `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>`,
  ],
  [
    "xl/styles.xml",
    `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2">
    <font><sz val="11"/><name val="Calibri"/></font>
    <font><b/><sz val="11"/><name val="Calibri"/></font>
  </fonts>
  <fills count="3">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFE9C46A"/><bgColor indexed="64"/></patternFill></fill>
  </fills>
  <borders count="2">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border><left style="thin"><color rgb="FFD9D9D9"/></left><right style="thin"><color rgb="FFD9D9D9"/></right><top style="thin"><color rgb="FFD9D9D9"/></top><bottom style="thin"><color rgb="FFD9D9D9"/></bottom><diagonal/></border>
  </borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="3">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
  </cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>`,
  ],
  [
    "xl/worksheets/sheet1.xml",
    `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>
  <cols>
    <col min="1" max="1" width="8" customWidth="1"/>
    <col min="2" max="2" width="24" customWidth="1"/>
    <col min="3" max="3" width="56" customWidth="1"/>
    <col min="4" max="4" width="110" customWidth="1"/>
  </cols>
  <sheetData>${sheetData}</sheetData>
  <autoFilter ref="A1:D${rows.length}"/>
</worksheet>`,
  ],
]);

const crcTable = new Uint32Array(256);

for (let index = 0; index < 256; index += 1) {
  let current = index;

  for (let bit = 0; bit < 8; bit += 1) {
    current = current & 1 ? 0xedb88320 ^ (current >>> 1) : current >>> 1;
  }

  crcTable[index] = current >>> 0;
}

const crc32 = (buffer) => {
  let crc = 0xffffffff;

  for (const byte of buffer) {
    crc = crcTable[(crc ^ byte) & 0xff] ^ (crc >>> 8);
  }

  return (crc ^ 0xffffffff) >>> 0;
};

const uint16 = (value) => {
  const buffer = Buffer.alloc(2);
  buffer.writeUInt16LE(value);
  return buffer;
};

const uint32 = (value) => {
  const buffer = Buffer.alloc(4);
  buffer.writeUInt32LE(value >>> 0);
  return buffer;
};

const dosDateTime = (date) => {
  const time =
    (date.getHours() << 11) | (date.getMinutes() << 5) | Math.floor(date.getSeconds() / 2);
  const dosDate =
    ((date.getFullYear() - 1980) << 9) | ((date.getMonth() + 1) << 5) | date.getDate();

  return { time, date: dosDate };
};

const zipEntries = [];
const localParts = [];
let offset = 0;
const now = dosDateTime(new Date());

for (const [name, content] of files) {
  const nameBuffer = Buffer.from(name, "utf8");
  const data = Buffer.from(content.trim(), "utf8");
  const compressed = zlib.deflateRawSync(data);
  const crc = crc32(data);

  const localHeader = Buffer.concat([
    uint32(0x04034b50),
    uint16(20),
    uint16(0),
    uint16(8),
    uint16(now.time),
    uint16(now.date),
    uint32(crc),
    uint32(compressed.length),
    uint32(data.length),
    uint16(nameBuffer.length),
    uint16(0),
    nameBuffer,
  ]);

  localParts.push(localHeader, compressed);
  zipEntries.push({
    nameBuffer,
    crc,
    compressedSize: compressed.length,
    size: data.length,
    offset,
  });
  offset += localHeader.length + compressed.length;
}

const centralParts = [];
let centralSize = 0;

for (const entry of zipEntries) {
  const centralHeader = Buffer.concat([
    uint32(0x02014b50),
    uint16(20),
    uint16(20),
    uint16(0),
    uint16(8),
    uint16(now.time),
    uint16(now.date),
    uint32(entry.crc),
    uint32(entry.compressedSize),
    uint32(entry.size),
    uint16(entry.nameBuffer.length),
    uint16(0),
    uint16(0),
    uint16(0),
    uint16(0),
    uint32(0),
    uint32(entry.offset),
    entry.nameBuffer,
  ]);

  centralParts.push(centralHeader);
  centralSize += centralHeader.length;
}

const endRecord = Buffer.concat([
  uint32(0x06054b50),
  uint16(0),
  uint16(0),
  uint16(zipEntries.length),
  uint16(zipEntries.length),
  uint32(centralSize),
  uint32(offset),
  uint16(0),
]);

fs.mkdirSync(outputDir, { recursive: true });
fs.writeFileSync(outputPath, Buffer.concat([...localParts, ...centralParts, endRecord]));

console.log(`Exported ${faqs.length} FAQ rows to ${outputPath}`);
