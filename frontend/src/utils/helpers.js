import {
  FileText,
  BarChart3,
  Link,
  Database,
} from "lucide-react";

export const getFileCategory = (filename) => {
  const ext = filename.split(".").pop().toLowerCase();

  if (["pdf", "docx", "txt"].includes(ext)) return "document";
  if (["xlsx", "xls", "csv"].includes(ext)) return "structured";

  return null;
};

export const SOURCE_ICONS = {
  document: FileText,
  structured: BarChart3,
  sheets: Link,
  database: Database,
};

export const SOURCE_LABELS = {
  document: "Document",
  structured: "Spreadsheet",
  sheets: "Google Sheets",
  database: "SQL Database",
};

export const getModeColor = (srcs) => {
  const hasS = srcs.some((s) =>
    ["structured", "sheets", "database"].includes(s.type)
  );

  const hasD = srcs.some((s) => s.type === "document");

  if (hasS && hasD) return "#a78bfa";
  if (hasS) return "#839705";

  return "#06b6d4";
};

let _counter = 0;

export const nextId = () => ++_counter;