import {FileText} from "lucide-react";

function ProcessingScreen({ status, onCancel }) {
  return (
    <div
      className="flex-1 flex items-center justify-center p-10 relative anim-fadeUp"
      style={{ background: "linear-gradient(160deg,#f8f6f0 0%,#eae7dc 60%,#ddd9cc 100%)" }}
    >
      {/* Grid overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage: "linear-gradient(rgba(131,151,5,0.06) 1px,transparent 1px),linear-gradient(90deg,rgba(131,151,5,0.06) 1px,transparent 1px)",
          backgroundSize: "48px 48px",
        }}
        aria-hidden
      />
 
      <div
        className="relative flex flex-col items-center gap-5 text-center w-full"
        style={{
          background: "#313e17",
          borderRadius: 24,
          padding: "52px 48px",
          maxWidth: 440,
          boxShadow: "0 10px 25px rgba(0,0,0,0.25), 0 4px 10px rgba(0,0,0,0.15)",
        }}
      >
        {/* Spinning ring */}
        <div className="relative flex items-center justify-center" style={{ width: 90, height: 90 }}>
          <svg width="90" height="90" viewBox="0 0 90 90" fill="none">
            <circle cx="45" cy="45" r="38" stroke="rgba(131,151,5,0.15)" strokeWidth="6"/>
            <circle cx="45" cy="45" r="38" stroke="url(#procGrad)" strokeWidth="6"
              strokeLinecap="round" strokeDasharray="68 172"
              className="anim-spin" style={{ transformOrigin: "45px 45px" }}
            />
            <defs>
              <linearGradient id="procGrad" x1="0" y1="0" x2="90" y2="90" gradientUnits="userSpaceOnUse">
                <stop stopColor="#000000"/>
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute text-3xl" style={{ animation: "dotPulse 2s ease infinite" }}>
            <div className="" style={{ color:"#000000",fontweight:"bold"}}>
              <FileText size={40}/>
            </div>
          </div>
        </div>
 
        <h2 className="font-display text-2xl tracking-widest" style={{ color: "#d8dfc4",textShadow: "1px 1px 3px rgba(0,0,0,0.8)" }}>
          PREPARING YOUR DOCUMENT
        </h2>
        <p className="font-ui font-semibold tracking-wide" style={{ fontSize: 15, color: "#000000", minHeight: 20,fontWeight:600 }}>
          {status}
        </p>
        <p className="font-body leading-relaxed" style={{ fontSize: 13, color: "rgba(216,223,196,0.6)" }}>
          Your file is being chunked, embedded, and indexed.<br/>
          This usually takes 10–30 seconds.
        </p>
 
 
        <button
          onClick={onCancel}
          className="font-ui font-bold uppercase tracking-widest cursor-pointer transition-all mt-1"
          style={{
            padding: "9px 28px", borderRadius: 10,
            border: "1px solid rgba(255,255,255,0.15)",
            background: "#505433",
            color: "#ffffff",
            boxShadow: "0 2px 8px rgba(0,0,0,0.5)",
            fontSize: 12, letterSpacing: "1px",
          }}
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

import { useState, useEffect, useRef } from "react";
import GlobalStyles  from "./components/GlobalStyles";
import Topbar        from "./components/Topbar";
import UploadPage    from "./components/UploadPage";
import ChatInterface from "./components/ChatInterface";
import { sendQuery, getDocumentStatus } from "./services/api";

export default function App() {
  const [phase, setPhase]         = useState("upload");
  const [sources, setSources]     = useState([]);
  const [activeIds, setActiveIds] = useState([]);
  const [messages, setMessages]   = useState([]);
  const [input, setInput]         = useState("");
  const [thinking, setThinking]   = useState(false);
  const [processingStatus, setProcessingStatus] = useState("");
  const pollRef = useRef(null);

const handleStartChat = () => {
  setMessages([]);

  const activeSources = sources.filter(
    (s) => activeIds.includes(s.id) && s.serverId
  );

  const docSources = activeSources.filter(
    (s) => s.type === "document"
  );

  // No documents → go directly to chat
  if (docSources.length === 0) {
    setPhase("chat");
    return;
  }

  setPhase("processing");

  setProcessingStatus(
    "Extracting text from your document…"
  );

  let attempt = 0;

  const MAX_ATTEMPTS = 12;

  const steps = [
    "Extracting text from your document…",
    "Splitting into chunks…",
    "Generating embeddings…",
    "Storing in vector database…",
    "Almost ready…",
  ];

  pollRef.current = setInterval(async () => {

    attempt++;

    setProcessingStatus(
      steps[Math.min(attempt - 1, steps.length - 1)]
    );

    try {

      const statuses = await Promise.all(
        docSources.map((s) =>
          getDocumentStatus(s.serverId)
        )
      );

      const allReady = statuses.every(
        (st) => st === 1
      );

      const anyFailed = statuses.some(
        (st) => st === 2
      );

      // Any failed
      if (anyFailed) {

        clearInterval(pollRef.current);

        setProcessingStatus(
          "❌ Document processing failed."
        );

        return;
      }

      // All ready
      if (allReady) {

        clearInterval(pollRef.current);

        setPhase("chat");

        return;
      }

      // Timeout protection
      if (attempt >= MAX_ATTEMPTS) {

        clearInterval(pollRef.current);

        setProcessingStatus(
          "Processing is taking longer than expected."
        );
      }

    } catch (err) {

      console.error("Polling error:", err);

      clearInterval(pollRef.current);

      setProcessingStatus(
        "❌ Failed to check document status."
      );
    }

  }, 5000); // Poll every 5 sec
};

  const handleBack = () => { if (pollRef.current) clearInterval(pollRef.current); setPhase("upload"); };
  useEffect(()=>()=>clearInterval(pollRef.current),[]);

  const handleSend = async () => {
    if (!input.trim()||thinking) return;
    const text = input.trim();
    setInput("");
    setMessages(p=>[...p,{role:"user",text}]);
    setThinking(true);
    const activeSources = sources.filter(s=>activeIds.includes(s.id)&&s.serverId);
    const structuredSrc = activeSources.find(s=>["structured","sheets","database"].includes(s.type));
    const docSrc        = activeSources.find(s=>s.type==="document");
    try {
      const res = await sendQuery({ query:text, data_source_id:structuredSrc?.serverId??null, document_id:docSrc?.serverId??null });
      setMessages(p=>[...p,{role:"assistant",text:res.data.answer,ms:res.data.exec_time_ms}]);
    } catch {
      setMessages(p=>[...p,{role:"assistant",text:"Something went wrong. Please try again.",error:true}]);
    } finally { setThinking(false); }
  };

  return (
    <div className="relative flex flex-col overflow-hidden" style={{ height:"100vh", background:"#f4f2ec", color:"#1a1f0a", fontFamily:"'Barlow',system-ui,sans-serif" }}>
      <GlobalStyles/>
      <Topbar phase={phase} onBack={handleBack}/>
      {phase==="upload"     && <UploadPage sources={sources} setSources={setSources} activeIds={activeIds} setActiveIds={setActiveIds} onStartChat={handleStartChat}/>}
      {phase==="processing" && <ProcessingScreen status={processingStatus} onCancel={handleBack}/>}
      {phase==="chat"       && <ChatInterface sources={sources} activeIds={activeIds} messages={messages} input={input} thinking={thinking} onInput={setInput} onSend={handleSend}/>}
    </div>
  );
}