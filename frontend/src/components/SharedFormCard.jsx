export default function FormCard({ title, sub, fields, error, loading, valid, onSubmit, btnLabel, btnColor }) {
  return (
    <div
      className="flex flex-col gap-3 rounded-2xl p-5"
      style={{ background:"rgba(255,255,255,0.04)", border:"1px solid rgba(255,255,255,0.1)" }}
    >
      <p className="font-display tracking-widest" style={{ fontSize:16, color:"#d8dfc4" }}>{title}</p>
      <p className="font-body" style={{ fontSize:12, color:"rgba(216,223,196,0.6)", marginTop:-6 }}>{sub}</p>
      {fields.map(f => (
        <div key={f.label} className="flex flex-col gap-1">
          <label className="font-ui font-bold uppercase tracking-widest" style={{ fontSize:10, color:"rgba(216,223,196,0.6)" }}>{f.label}</label>
          <input
            className="w-full font-body rounded-lg px-3 py-2"
            style={{ background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.15)", color:"#d8dfc4", fontSize:13 }}
            value={f.value} onChange={e=>f.onChange(e.target.value)} placeholder={f.placeholder}
          />
          {f.hint && <p className="font-ui tracking-wide" style={{ fontSize:10, color:"rgba(216,223,196,0.5)" }}>{f.hint}</p>}
        </div>
      ))}
      {error && (
        <p className="font-body rounded-lg px-3 py-2" style={{ fontSize:12, color:"#fca5a5", background:"rgba(239,68,68,0.1)", border:"1px solid rgba(239,68,68,0.2)" }}>
          {error}
        </p>
      )}
      <button
        onClick={onSubmit} disabled={!valid||loading}
        className="flex items-center justify-center gap-2 font-ui font-bold uppercase tracking-widest cursor-pointer rounded-lg py-2.5 mt-1 transition-opacity"
        style={{ background:btnColor, color:"#fff", fontSize:12, letterSpacing:"1.5px", opacity:(!valid||loading)?0.4:1 }}
      >
        {loading ? <><Spinner size={14} color="#fff"/> Connecting…</> : btnLabel}
      </button>
    </div>
  );
}