import { useEffect, useRef } from "react";
import Spinner from "./Spinner";
import { SOURCE_ICONS } from "../utils/helpers";

export default function ChatInterface({ sources, activeIds, messages, input, thinking, onInput, onSend }) {
  const bottomRef = useRef(null);
  const textRef   = useRef(null);
 
  const activeSources = sources.filter(s=>activeIds.includes(s.id));
  const hasStructured = activeSources.some(s=>["structured","sheets","database"].includes(s.type));
 
  useEffect(()=>{ bottomRef.current?.scrollIntoView({ behavior:"smooth" }); },[messages,thinking]);
  useEffect(()=>{ textRef.current?.focus(); },[]);
 
  const onKey = (e) => { if (e.key==="Enter"&&!e.shiftKey){ e.preventDefault(); onSend(); } };
 
  const suggestions = hasStructured
    ? ["Summarise overall trends","Detect anomalies","Calculate key KPIs","Financial health score"]
    : ["Summarise this document","What are the main topics?","Key findings or conclusions","Compare sections"];
 
  return (
    <div
      className="flex-1 flex flex-col overflow-hidden"
      style={{ background:"linear-gradient(160deg,#f8f6f0 0%,#eae7dc 60%,#ddd9cc 100%)" }}
    >
      {/* Sources bar */}
      <div
        className="flex items-center gap-1 flex-wrap flex-shrink-0 px-7 py-2.5"
        style={{ background:"#ffffff" }}
      >
        
        <div className="flex gap-1 flex-wrap">
          {activeSources.map(src=>(
            <span
              key={src.id}
              className="flex items-center gap-1 font-ui font-semibold tracking-wide"
              style={{ fontSize:11, padding:"3px 10px", borderRadius:20, margin:"5px 5px",border:"1px solid rgba(131,151,5,0.4)", color:"#9db006", background:"rgba(131,151,5,0.12)" }}
            >
              {
                (() => {
                  const Icon = SOURCE_ICONS[src.type];
                  return Icon ? <Icon size={14} /> : null;
                })()
              }

              {src.name}
            </span>
          ))}
        </div>
      </div>
 
      {/* Messages */}
      <div className="flex-1 overflow-y-auto flex flex-col gap-4" style={{ padding:"28px 32px" }}>
        {messages.length===0 && (
          <div className="flex-1 flex flex-col items-center justify-center text-center anim-fadeUp" style={{ padding:"60px 20px" }}>
            <div className="font-display mb-4" style={{ fontSize:48, color:"#839705" }}>✦</div>
            <h3 className="font-display font-normal tracking-widest mb-2" style={{ fontSize:28, letterSpacing:"2px", color:"#000000", fontWeight:600,textShadow: "1px 1px 3px rgba(0,0,0,0.4)" }}>
              Ready to Analyse
            </h3>
            <p className="font-body mb-6" style={{ fontSize:14, color:"#5a6040",textshadow: "1px 1px 2px rgba(0,0,0,0.5)",fontWeight:600,marginBottom:20 }}>
              Ask anything about your data, or try one of these:
            </p>
            <div className="flex gap-2 flex-wrap justify-center">
              {suggestions.map(c=>(
                <button
                  key={c}
                  className="suggestion-chip font-body cursor-pointer transition-all"
                  onClick={()=>onInput(c)}
                  style={{ padding:"7px 16px", borderRadius:20, border:"1px solid rgba(0,0,0,0.12)", background:"#505433", color:"#ffffff", fontSize:13 }}
                >{c}</button>
              ))}
            </div>
          </div>
        )}
 
        {messages.map((m,i)=>(
          <div
            key={i}
            className="flex anim-msgIn"
            style={{ justifyContent:m.role==="user"?"flex-end":"flex-start", animationDelay:`${i*0.03}s` }}
          >
            <div
              className="font-body leading-relaxed whitespace-pre-wrap break-words"
              style={{
                maxWidth:"70%", padding:"12px 16px", fontSize:14, lineHeight:1.7,
                borderRadius: m.role==="user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
                background: m.role==="user" ? "#41431B" : m.error ? "rgba(239,68,68,0.08)" : "rgba(255,255,255,0.85)",
                color: m.role==="user" ? "#d8dfc4" : m.error ? "#c53030" : "#1a1f0a",
                border: m.role==="user" ? "none" : `1px solid ${m.error?"rgba(239,68,68,0.2)":"rgba(0,0,0,0.08)"}`,
                boxShadow: m.role==="user" ? "0 4px 16px rgba(65,67,27,0.3)" : "0 2px 12px rgba(0,0,0,0.06)",
                backdropFilter: m.role!=="user" ? "blur(8px)" : undefined,
              }}
            >
              {m.text}
              {m.ms && (
                <span className="block mt-1.5 font-ui font-semibold tracking-wide text-right" style={{ fontSize:10, color:"rgba(0,0,0,0.2)" }}>
                  {(m.ms/1000).toFixed(1)}s
                </span>
              )}
            </div>
          </div>
        ))}
 
        {thinking && (
          <div className="flex">
            <div
              className="flex items-center"
              style={{ padding:"12px 16px", borderRadius:"18px 18px 18px 4px", background:"rgba(255,255,255,0.85)", border:"1px solid rgba(0,0,0,0.08)" }}
            >
              <div className="flex gap-1 items-center" style={{ height:20, padding:"0 4px" }}>
                <span className="dot-bounce"/><span className="dot-bounce"/><span className="dot-bounce"/>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef}/>
      </div>
 
      {/* Input area */}
      <div
        className="flex-shrink-0"
        style={{ padding:"16px 32px 22px", borderTop:"1px solid rgba(0,0,0,0.08)", background:"rgba(248,246,240,0.9)", backdropFilter:"blur(12px)" }}
      >
        <div
          className="flex items-end gap-2.5 rounded-2xl"
          style={{ background:"#505433", border:"1px solid rgba(0,0,0,0.12)", padding:"10px 10px 10px 16px", boxShadow:"0 2px 8px rgba(0,0,0,0.06)" }}
        >
          <textarea
            ref={textRef}
            className="flex-1 font-body border-0 bg-transparent resize-none "
            style={{ color:"#ffffff", fontSize:14, lineHeight:1.6, minHeight:30, maxHeight:140, outline:"none",textShadow: "2px 2px 2px rgba(0,0,0,0.4)"}}
            value={input}
            onChange={e=>onInput(e.target.value)}
            onKeyDown={onKey}
            placeholder="Ask a question about your data..."
            rows={1}
          />
          <button
            onClick={onSend}
            disabled={!input.trim()||thinking}
            className="flex items-center justify-center flex-shrink-0 rounded-xl border-0 cursor-pointer transition-all"
            style={{
              width:36, height:36, background:"#41431B", color:"#fff",
              opacity:(!input.trim()||thinking)?0.35:1,
            }}
          >
            {thinking
              ? <Spinner size={14} color="#fff"/>
              : <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <line x1="22" y1="2" x2="11" y2="13"/>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
            }
          </button>
        </div>
        <p className="font-ui tracking-wide text-center mt-2" style={{ fontSize:12, color:"#929292", letterSpacing:"0.5px",textShadow: "2px 2px 2px rgba(0,0,0,0.1)", fontWeight:600 }}>
          Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}