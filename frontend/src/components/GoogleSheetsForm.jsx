import {useState} from "react";
import FormCard from "./SharedFormCard";

export default function GoogleSheetsForm({ onConnect }) {
  const [url, setUrl]     = useState("");
  const [sheet, setSheet] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
 
  const handleSubmit = async () => {
    if (!url.trim()) return;
    setError(""); setLoading(true);
    try {
      await onConnect(url.trim(), sheet.trim() || null);
      setUrl(""); setSheet("");
    } catch(e) {
      setError(e?.response?.data?.detail || "Could not connect. Check the URL and try again.");
    } finally { setLoading(false); }
  };
 
  const valid = url.trim().includes("docs.google.com/spreadsheets");
  return <FormCard title="Connect a Google Sheet" sub="Sheet must be accessible via link (no sign-in required)"
    fields={[
      { label:"Spreadsheet URL *", value:url, onChange:setUrl, placeholder:"https://docs.google.com/spreadsheets/d/…" },
      { label:"Sheet / Tab name (optional)", value:sheet, onChange:setSheet, placeholder:"Sheet1 — leave blank for the first tab" },
    ]}
    error={error} loading={loading} valid={valid}
    onSubmit={handleSubmit} btnLabel="CONNECT SHEET" btnColor="#839705"
  />;
}