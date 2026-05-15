import {useState} from "react";
import FormCard from "./SharedFormCard";

export default function DatabaseForm({ onConnect }) {
  const [conn, setConn]   = useState("");
  const [table, setTable] = useState("");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
 
  const handleSubmit = async () => {
    if (!conn.trim() || !table.trim()) return;
    setError(""); setLoading(true);
    try {
      await onConnect(conn.trim(), table.trim(), query.trim() || null);
      setConn(""); setTable(""); setQuery("");
    } catch(e) {
      setError(e?.response?.data?.detail || "Connection failed. Check your credentials and try again.");
    } finally { setLoading(false); }
  };
 
  const valid = conn.trim() && table.trim();
  return <FormCard title="Connect a SQL Database" sub="PostgreSQL · MySQL · SQLite · MSSQL"
    fields={[
      { label:"Connection String *", value:conn, onChange:setConn, placeholder:"postgresql://user:pass@host:5432/dbname" },
      { label:"Table Name *", value:table, onChange:setTable, placeholder:"sales_data" },
      { label:"Custom SQL Query (optional)", value:query, onChange:setQuery, placeholder:"SELECT * FROM sales WHERE year = 2024", hint:"Leave blank to read the entire table" },
    ]}
    error={error} loading={loading} valid={!!valid}
    onSubmit={handleSubmit} btnLabel="CONNECT DATABASE" btnColor="#d97706"
  />;
}