import { SOURCE_ICONS, SOURCE_LABELS } from "../utils/helpers";
import {X,Check,File} from "lucide-react";
import Spinner from "./Spinner";

export default function SourceCard({ source, selected, onToggle }) {
  const { name, type, status } = source;
  const isReady   = status === "ready";
  const isLoading = status === "uploading";
  const isError   = status === "error";
  const Icon = SOURCE_ICONS[type] || File;
 
  return (
    <div
      className="source-card flex items-center justify-between px-3.5 py-2.5 rounded-xl transition-all anim-slideIn"
      style={{
        border: `1px solid ${selected ? "rgba(131,151,5,0.5)" : isError ? "rgba(248,113,113,0.3)" : "rgba(255,255,255,0.1)"}`,
        background: selected ? "rgba(131,151,5,0.12)" : isError ? "rgba(248,113,113,0.06)" : "rgba(255,255,255,0.05)",
        cursor: isReady ? "pointer" : "default",
      }}
      onClick={() => isReady && onToggle(source.id)}
    >
      <div className="flex items-center gap-2.5 min-w-0">
        <span style={{ flexShrink:0 }}>
          <Icon size={18} />
        </span>
        <div className="min-w-0">
          <p className="font-body font-medium truncate" style={{ fontSize:13, color:"#d8dfc4", maxWidth:220 }}>{name}</p>
          <p className="font-ui font-semibold uppercase tracking-wide mt-0.5" style={{ fontSize:10, color:"rgba(216,223,196,0.6)" }}>
            {SOURCE_LABELS[type] ?? type}
            {isLoading && " · uploading…"}
            {isError   && " · failed"}
          </p>
        </div>
      </div>
      <div className="flex items-center flex-shrink-0">
        {isLoading && <Spinner size={16} color="#839705"/>}
        {isError   && <span className="font-bold" style={{ color:"#f87171", fontSize:20,paddingRight:"10px" }}><X /></span>}
        {isReady   && (
          <div
            className="flex items-center justify-center rounded-md transition-all"
            style={{
              paddingRight:"15px", fontSize:18, color:"#fff",
            }}
          >
            {selected && "✔"}
          </div>
        )}
      </div>
    </div>
  );
}