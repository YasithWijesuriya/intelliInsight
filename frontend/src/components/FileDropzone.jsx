import {useState, useRef} from "react";
import Spinner from "./Spinner";
import { Upload } from "lucide-react";

export default function FileDropzone({ onFiles, uploading }) {
  const [dragging, setDragging] = useState(false);
  const ref = useRef(null);
 
  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer.files.length) onFiles(e.dataTransfer.files);
  };
 
  const zoneBase = "flex flex-col items-center gap-2 text-center cursor-pointer transition-all duration-200 rounded-2xl";
  const zoneDrag = dragging ? "scale-[1.01]" : "";
 
  return (
    <div
      className={`${zoneBase} ${zoneDrag}`}
      style={{
        border:`2px dashed ${dragging ? "#8b8989" : "#1d1c1c"}`,
        borderRadius: 50, padding: "36px 24px",margin:"0px 60px",
        background: dragging ? "#313e17" : "#ffffff",
        userSelect: "none",
        cursor: uploading ? "default" : "pointer",
        borderStyle: uploading ? "solid" : "dashed",
        borderColor: uploading ? "rgba(131,151,5,0.5)" : undefined,
      }}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => !uploading && ref.current?.click()}
    >
      <input
        ref={ref} type="file" multiple
        className="hidden"
        accept=".pdf,.docx,.txt,.xlsx,.xls,.csv"
        onChange={(e) => e.target.files?.length && onFiles(e.target.files)}
      />
      {uploading ? (
        <>
          <Spinner size={28} color="#067017" />
          <p className="font-display tracking-wide" style={{ fontSize:16, color:"#000000" }}>Uploading…</p>
        </>
      ) : (
        <>
          <div style={{ color: dragging ? "#313e17" : "#ffffff",
            border:"2px solid",
            borderColor: dragging ? "#ffffff" : "#000000",
              borderRadius: "50%",              padding: 8,
              background: dragging ? "#ffffff" : "#000000",          
            transition:"color 0.2s,transform 0.2s", transform: dragging?"translateY(-4px)":"none" }}>
            <Upload size={32} strokeWidth={1.5} />
          </div>
          <p className="font-display tracking-wide" style={{ fontSize:16,
          fontWeight: 600,  
          fontFamily:"'Raleway', sans-serif", letterSpacing:"0.5px",color: dragging ? "#ffffff" : "#00000077", transition:"color 0.2s,transform 0.2s" }}>
            {dragging ? "Drop to upload" : "Drag & drop your files here"}
          </p>
          <p className="font-body" style={{ fontSize:13,
            fontWeight: 600,
            fontFamily:"'Montserrat', sans-serif", color: dragging ? "#ffffff" : "#00000066", marginTop:-2 }}>or click to browse</p>
          <p className="font-ui uppercase tracking-widest mt-1" style={{ fontSize:12,
          fontWeight: 600, letterSpacing:"1.5px",  
          color: dragging ? "#ffffff" : "#00000099" }}>
            PDF · DOCX · TXT · XLSX · XLS · CSV
          </p>
        </>
      )}
    </div>
  );
}