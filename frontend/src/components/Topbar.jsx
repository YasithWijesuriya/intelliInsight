import {ArrowLeft} from "lucide-react";
import logo from "/logo/intelli_agent_logo.png"

export default function Topbar({ phase, onBack }) {
  return (
    <header
      className="flex items-center justify-between flex-shrink-0 px-7 z-20 relative"
      style={{ height: 100, background: "#313E17",boxShadow: "0 2px 10px rgba(0,0,0,0.8)" }}
    >
      {/* Logo row */}
      <div className="flex items-center gap-8 flex-1">
        <div className="flex items-center">
            <div className="flex flex-col  items-center justify-center" style={{ paddingTop:"10px" }}>
              <img src={logo} alt="IntelliInsight" style={{ height:"120px",
                
              }} 
            
              />
            </div>
        </div>

      </div>
 
      {/* Right actions */}
      <div className="flex items-center gap-2">
        {phase === "chat" && (
          <button
              className="flex flex-row items-center gap-2 font-ui cursor-pointer transition-all duration-300 hover:bg-black"
              onClick={onBack}
              style={{
                background: "#505433",
                border: "1px solid #ffffff",
                color: "#ffffff",
                fontSize: 12,
                fontWeight: 600,
                letterSpacing: "0.5px",
                padding: "7px 14px",
                borderRadius: 10,
              }}
            >
              <ArrowLeft size={18} color="#ffffff" />
              <span>Back to sources</span>
        </button>
        )}
        <button
          className="flex items-center gap-2 font-ui cursor-pointer transition-all"
          style={{
            background: "#000000",
            border: "1px solid #ffffff",
            color: "#ffffff",
            fontSize: 11, fontWeight: 700, letterSpacing: "1.2px",
            padding: "8px 16px", borderRadius: 30,
          }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0"/>
          </svg>
          NOTIFICATIONS
        </button>
        <button
          className="font-ui cursor-pointer transition-all"
          style={{
            background: "#000000",
            border: "1px solid #ffffff",
            color: "#ffffff",
            fontSize: 12, fontWeight: 700, letterSpacing: "1.5px",
            padding: "8px 22px", borderRadius: 30,
          }}
        >
          LOG IN
        </button>
      </div>
    </header>
  );
}