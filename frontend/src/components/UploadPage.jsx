import { useState } from "react";
import Robot3D from "./Robot3D";
import FileDropzone from "./FileDropzone";
import SourceCard from "./SourceCard";
import {uploadDocument, uploadStructured, connectGoogleSheets, connectDatabase} from "../services/api";
import GoogleSheetsForm from "./GoogleSheetsForm";
import DatabaseForm from "./DatabaseForm";
import {Link, Database,ArrowRight,FileText} from "lucide-react"
import {
  getFileCategory,
  nextId,
} from "../utils/helpers";

export default function UploadPage({ sources, setSources, activeIds, setActiveIds, onStartChat }) {
  const [tab, setTab]           = useState("files");
  const [anyUploading, setAnyUploading] = useState(false);
 
  const addSource   = (src)     => setSources(p=>[...p,src]);
  const patchSource = (id,obj)  => setSources(p=>p.map(s=>s.id===id?{...s,...obj}:s));
  const toggleSelect = (id)     => setActiveIds(p=>p.includes(id)?p.filter(x=>x!==id):[...p,id]);
 
  const handleFiles = async (fileList) => {
    const files = Array.from(fileList);
    setAnyUploading(true);
    await Promise.all(files.map(async(file)=>{
      const type = getFileCategory(file.name);
      if (!type) return;
      const id = nextId();
      addSource({ id, name:file.name, type, status:"uploading", serverId:null });
      try {
        const res = type==="document" ? await uploadDocument(file) : await uploadStructured(file);
        patchSource(id,{ status:"ready", serverId:res.data.id });
        setActiveIds(p=>[...p,id]);
      } catch (err) {
        console.error("Upload failed:", err);

        patchSource(id, {
          status: "error"
        }); }
    }));
    setAnyUploading(false);
  };
 
  const handleSheets = async (url, sheetName) => {
    const id = nextId();
    const shortName = "Sheet: "+(url.split("/d/")[1]?.slice(0,14)??"…")+"…";
    addSource({ id, name:shortName, type:"sheets", status:"uploading", serverId:null });
    try {
      const res = await connectGoogleSheets(url,sheetName);
      patchSource(id,{ status:"ready", serverId:res.data.id, name:`Sheet: ${res.data.sheet_id?.slice(0,12)}…` });
      setActiveIds(p=>[...p,id]);
    } catch(e) { patchSource(id,{status:"error"}); throw e; }
  };
 
  const handleDB = async (connStr,tableName,query) => {
    const id = nextId();
    addSource({ id, name:`DB: ${tableName}`, type:"database", status:"uploading", serverId:null });
    try {
      const res = await connectDatabase(connStr,tableName,query);
      patchSource(id,{ status:"ready", serverId:res.data.id });
      setActiveIds(p=>[...p,id]);
    } catch(e) { patchSource(id,{status:"error"}); throw e; }
  };
 
  const readySources   = sources.filter(s=>s.status==="ready");
  const loadingSources = sources.filter(s=>s.status==="uploading");
  const selectedReady  = readySources.filter(s=>activeIds.includes(s.id));
  const canStart = selectedReady.length > 0;
 
const TABS = [
  {
    id: "files",
    label: (
      <span className="flex items-center gap-2">
        <FileText size={20} />
        Files
      </span>
    ),
  },
  {
    id: "sheets",
    label: (
      <span className="flex items-center gap-2">
        <Link size={20} />
        Google Sheets
      </span>
    ),
  },
  {
    id: "db",
    label: (
      <span className="flex items-center gap-2">
        <Database size={20} />
        Database
      </span>
    ),
  },
];
 
  return (
    <div className="flex-1 grid overflow-hidden" style={{ gridTemplateColumns:"1fr 1.05fr",background:"#e1e1e1" }}>
 
      <div
        className="absolute inset-0 pointer-events-none"
        style={{ backgroundImage:"linear-gradient(rgba(131,151,5,0.04) 1px,transparent 1px),linear-gradient(90deg,rgba(131,151,5,0.07) 1px,transparent 1px)", backgroundSize:"48px 48px" }}
        aria-hidden
      />
      {/* ── LEFT hero panel ── */}
      <section
        className="relative flex flex-col justify-between overflow-hidden"
        style={{ background:"rgb(225, 225, 225)", padding:"48px 30px 0" }}
      >
        {/* Grid overlay */}
 
        {/* Hero content */}
        <div className="relative z-10 flex flex-col gap-5">
          
          <h1 className="font-display leading-none tracking-wide" style={{ fontSize:52, color:"#000000",fontFamily:"Russo One, sans-serif"}}>
            TURN DATA INTO<br/>
            <span style={{ color:"#313e17" }}>CLEAR INSIGHT</span>
          </h1>
          <p className="font-body leading-relaxed" style={{ fontSize:14, color:"#3c3c3c", maxWidth:230, lineHeight:1.95,fontWeight:500 }}>
            Upload your datasets and let the AI surface what matters.
            Ask questions in plain English and explore analytics visually
            — all in one place.
          </p>
 
          {/* Feature pills */}
          <div className="flex flex-col gap-2  mt-1">
            {["Financial Analysis","Document Q&A","Live Sources","Anomaly Detection"].map(f=>(
              <span
                key={f}
                className="font-ui font-semibold uppercase tracking-widest"
                style={{ fontSize:11, letterSpacing:"0.8px", padding:"5px 12px",
                width:"max-content",
                borderRadius:20, border:"1px solid #000000", color:"#000000", background:"rgba(49, 62, 23, 0.1)" }}
              >{f}</span>
            ))}
          </div>
        </div>
 
        {/* Robot */}
        <div
          className="flex justify-center items-start flex-1 min-h-0 anim-roboGlow"
          style={{
            alignItems: "center",
          }}
          >
          <Robot3D />
        </div>
      </section>
 
      {/* ── RIGHT olive card ── */}
      <section
        className="flex flex-row  overflow-hidden  realtive"
        style={{ background:"#505433",borderRadius:"40px",margin:"20px"}}
      >
        <div className="overflow-y-auto scroll-smooth w-full h-full">
    
        <div className="flex-1 flex flex-col gap-4" style={{ padding:"20px 36px 32px" }}>
          <h2 className="font-display text-center animate-pulse
    drop-shadow-[0_0_0.5px_white]" style={{ fontSize:40, letterSpacing:"4px", 
          textShadow: "2px 2px 4px rgba(0,0,0,0.8)",  
          color:"#ffffff" }}>
            ADD YOUR DATA
          </h2>
          
 
          {/* Tabs */}
          <div className="flex flex-wrap justify-center items-center gap-10">
            {TABS.map(t=>(
              <button
                key={t.id}
                className={`input-tab font-ui font-bold tracking-widest cursor-pointer transition-all px-4 py-2 ${tab===t.id?"active-tab":""}`}
                style={{
                  fontSize:13,
                  letterSpacing:"1px",
                  textShadow: "2px 2px 4px rgba(0,0,0,0.2",
                  border:`3px solid ${tab===t.id?"#ffff":"#000000"}`,
                  background: tab===t.id ? "#000000" : "rgba(255,255,255,0.06)",
                  padding:"3px 5px",
                  borderRadius:10,
                  color: tab===t.id ? "#ffff" : "#000000",
                }}
                onClick={()=>setTab(t.id)}
              >{t.label}</button>
            ))}
          </div>
 
          {/* Tab content */}
          <div>
            {tab==="files"  && <FileDropzone onFiles={handleFiles} uploading={anyUploading}/>}
            {tab==="sheets" && <GoogleSheetsForm onConnect={handleSheets}/>}
            {tab==="db"     && <DatabaseForm onConnect={handleDB}/>}
          </div>
 
          {/* Sources */}
          <div className="flex flex-col gap-1 flex-1">
            <p className="font-display tracking-widest" style={{ fontSize:18,fontFamily:"'Lato' ,sans-serif",letterSpacing:"2px", color:"#ffffff",
            textShadow: "2px 2px 2px rgba(0,0,0,0.8)",
            marginLeft:20,
             }}>Your Sources</p>
            <div className="flex flex-col gap-1.5" style={{ minHeight:60 }}>
              {sources.length===0 ? (
                <div
                  className="flex items-center gap-2.5 px-4 py-3.5 rounded-2xl"
                  style={{ background:"#656D3F", border:"1px solid #ffff", color:"rgba(253, 253, 253, 0.5)",
                  fontWeight:700,textShadow: "2px 2px 2px rgba(0,0,0,0.8)",
                  margin:"0px 20px",
                  padding:"15px 10px"
                   }}
            
                >
                <FileText size={18} />
                  <span className="font-ui font-medium tracking-wide" style={{ fontSize:13, letterSpacing:"1px",color:"rgba(253, 253, 253, 0.5)",fontWeight:700,textShadow: "2px 2px 2px rgba(0,0,0,0.1)"}}>
                    No sources added yet
                  </span>
                </div>
              ) : (
                sources.map(src=>(
                  <SourceCard key={src.id} source={src} selected={activeIds.includes(src.id)} onToggle={toggleSelect}/>
                ))
              )}
            </div>
 
            {loadingSources.length > 0 && (
              <div className="" style={{ fontSize:"12px", color:"#afaaaa", fontStyle:"italic", marginTop:2 }}>
                {loadingSources.length} source{loadingSources.length>1?"s":""} uploading…
              </div>
            )}
          </div>
 
          {/* Start button */}
          <button
            className="start-btn flex items-center justify-center gap-3 font-display tracking-widest rounded-2xl border-0 cursor-pointer transition-all mt-auto"
            style={{
              padding:"14px 24px",
              margin:"0px 40px",
              background:"#000000",
              color:"#ffffff",
              fontSize:14, letterSpacing:"2px",
              opacity: canStart ? 1 : 0.45,
              cursor: canStart ? "pointer" : "not-allowed",
            }}
            onClick={onStartChat}
            disabled={!canStart}
          >
            START TO ANALYSING
            <ArrowRight size={20} color="#ffffff" />
          </button>
 
          {!canStart && sources.length>0 && (
            <p className="font-ui text-center tracking-wide" style={{ fontSize:11, color:"rgba(216,223,196,0.5)", letterSpacing:"0.5px" }}>
              {loadingSources.length>0 ? "Wait for uploads to finish" : "Select at least one source above"}
            </p>
          )}
        </div>
        </div>
      </section>
    </div>
  );
}