export default function GlobalStyles() {
  return (
    <style>{`
      @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Special+Elite&family=Rajdhani:wght@400;500;600;700&family=Barlow:wght@300;400;500;600&display=swap');
      *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
      html, body, #root { height: 100%; background: #f4f2ec; color: #1a1f0a; font-family: 'Barlow', system-ui, sans-serif; }
 
      .font-display  { font-family: 'Bebas Neue', serif; }
      .font-stamp    { font-family: 'Special Elite', serif; }
      .font-ui       { font-family: 'Rajdhani', system-ui, sans-serif; }
      .font-body     { font-family: 'Barlow', system-ui, sans-serif; }
 
      ::-webkit-scrollbar { width: 4px; }
      ::-webkit-scrollbar-thumb { background: rgba(131,151,5,0.3); border-radius: 4px; }
      textarea, input { font-family: 'Barlow', system-ui, sans-serif; }
      textarea:focus, input:focus { outline: none; }
      button { font-family: 'Rajdhani', system-ui, sans-serif; }
 
      @keyframes spin      { to { transform: rotate(360deg); } }
      @keyframes fadeUp    { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }
      @keyframes msgIn     { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }
      @keyframes slideIn   { from { opacity:0; transform:translateX(-8px); } to { opacity:1; transform:translateX(0); } }
      @keyframes dotPulse  { 0%,80%,100% { transform:translateY(0); opacity:0.35; } 40% { transform:translateY(-5px); opacity:1; } }
      @keyframes roboFloat { 0%,100% { transform:translateY(0px) rotate(-1deg); } 50% { transform:translateY(-12px) rotate(1deg); } }
      @keyframes roboGlow  { 0%,100% { filter:drop-shadow(0 0 8px rgba(131,151,5,0.4)); } 50% { filter:drop-shadow(0 0 20px rgba(131,151,5,0.7)); } }
      @keyframes blink     { 0%,90%,100% { opacity:1; } 95% { opacity:0; } }
      @keyframes orb       { 0%,100% { transform:translate(0,0) scale(1); } 33% { transform:translate(30px,-20px) scale(1.04); } 66% { transform:translate(-15px,25px) scale(0.96); } }
 
      .anim-fadeUp    { animation: fadeUp 0.4s ease both; }
      .anim-msgIn     { animation: msgIn 0.22s ease both; }
      .anim-slideIn   { animation: slideIn 0.25s ease both; }
      .anim-roboFloat { animation: roboFloat 4s ease-in-out infinite; }
      .anim-roboGlow  { animation: roboGlow 3s ease-in-out infinite; }
      .anim-spin      { animation: spin 1.4s linear infinite; }
      .anim-spinFast  { animation: spin 0.7s linear infinite; }
      .anim-dotPulse  { animation: dotPulse 1.3s ease infinite; }
      .anim-blink     { animation: blink 3s ease infinite; }
 
      .dot-bounce { display:inline-block; width:6px; height:6px; border-radius:50%; background:#839705; animation:dotPulse 1.3s ease infinite; }
      .dot-bounce:nth-child(2) { animation-delay:0.15s; }
      .dot-bounce:nth-child(3) { animation-delay:0.30s; }
 
      .suggestion-chip:hover { background:rgba(131,151,5,0.15) !important; border-color:rgba(131,151,5,0.5) !important; color:#9db006 !important; }
      .source-card:hover { background:rgba(255,255,255,0.07) !important; border-color:rgba(131,151,5,0.3) !important; }
      .input-tab:hover:not(.active-tab) { background:rgba(255,255,255,0.08) !important; color:#d8dfc4 !important; }
      .start-btn:hover:not(:disabled) { opacity:0.85 !important; }
    `}</style>
  );
}