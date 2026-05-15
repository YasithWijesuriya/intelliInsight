// import { useState, useRef } from "react";
// import { uploadStructured, uploadDocument } from "@/services/api";

// export default function FileUpload({ onUploaded }) {
//   const [dragging, setDragging] = useState(false);
//   const [uploading, setUploading] = useState(false);
//   const [status, setStatus] = useState(null); // null | "success" | "error"
//   const [statusMsg, setStatusMsg] = useState("");
//   const inputRef = useRef(null);

//   const processFile = async (file) => {
//     if (!file) return;
//     setUploading(true);
//     setStatus(null);
//     const ext = file.name.split(".").pop().toLowerCase();
//     try {
//       if (["pdf", "docx", "txt"].includes(ext)) {
//         await uploadDocument(file);
//       } else {
//         await uploadStructured(file);
//       }
//       setStatus("success");
//       setStatusMsg(`${file.name} uploaded`);
//       onUploaded();
//       setTimeout(() => setStatus(null), 3000);
//     } catch {
//       setStatus("error");
//       setStatusMsg("Upload failed. Try again.");
//       setTimeout(() => setStatus(null), 4000);
//     } finally {
//       setUploading(false);
//     }
//   };

//   const onDrop = (e) => {
//     e.preventDefault();
//     setDragging(false);
//     const file = e.dataTransfer.files[0];
//     processFile(file);
//   };

//   return (
//     <div className="fu-root">
//       <div className="fu-label">Upload File</div>

//       <div
//         className={`fu-zone ${dragging ? "drag" : ""} ${uploading ? "uploading" : ""}`}
//         onDragOver={e => { e.preventDefault(); setDragging(true); }}
//         onDragLeave={() => setDragging(false)}
//         onDrop={onDrop}
//         onClick={() => !uploading && inputRef.current?.click()}
//       >
//         <input
//           ref={inputRef} type="file"
//           style={{ display: "none" }}
//           onChange={e => processFile(e.target.files[0])}
//           accept=".pdf,.docx,.txt,.xlsx,.xls,.csv"
//         />
//         {uploading ? (
//           <div className="fu-spinner" />
//         ) : (
//           <svg className="fu-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
//             <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" />
//           </svg>
//         )}
//         <span className="fu-text">
//           {uploading ? "Uploading…" : "Drop file or click"}
//         </span>
//         <span className="fu-sub">PDF · DOCX · TXT · XLSX · CSV</span>
//       </div>

//       {status && (
//         <div className={`fu-status ${status}`}>
//           {status === "success" ? "✓" : "✗"} {statusMsg}
//         </div>
//       )}

//       <style>{`
//         .fu-root { font-family: var(--font, 'DM Sans', system-ui); }
//         .fu-label {
//           font-size: 10px; font-weight: 600; letter-spacing: 1.1px;
//           text-transform: uppercase; color: rgba(232,234,240,0.35);
//           margin-bottom: 8px;
//         }
//         .fu-zone {
//           display: flex; flex-direction: column; align-items: center;
//           gap: 6px; padding: 18px 12px; border-radius: 10px;
//           border: 1px dashed rgba(255,255,255,0.15);
//           background: rgba(255,255,255,0.03);
//           cursor: pointer; text-align: center;
//           transition: border-color 0.2s, background 0.2s;
//         }
//         .fu-zone:hover, .fu-zone.drag {
//           border-color: rgba(99,102,241,0.5);
//           background: rgba(99,102,241,0.07);
//         }
//         .fu-zone.uploading { cursor: default; border-style: solid; }
//         .fu-icon { color: rgba(232,234,240,0.35); }
//         .fu-text { font-size: 12px; color: rgba(232,234,240,0.5); font-weight: 500; }
//         .fu-sub { font-size: 10px; color: rgba(232,234,240,0.25); letter-spacing: 0.3px; }
//         .fu-spinner {
//           width: 20px; height: 20px; border-radius: 50%;
//           border: 2px solid rgba(255,255,255,0.1);
//           border-top-color: #6366f1;
//           animation: spin 0.7s linear infinite;
//         }
//         @keyframes spin { to { transform: rotate(360deg); } }
//         .fu-status {
//           margin-top: 8px; font-size: 11px; padding: 6px 10px;
//           border-radius: 6px; animation: fadeUp 0.2s ease;
//         }
//         @keyframes fadeUp {
//           from { opacity: 0; transform: translateY(4px); }
//           to { opacity: 1; transform: translateY(0); }
//         }
//         .fu-status.success {
//           background: rgba(16,185,129,0.12); color: #6ee7b7;
//           border: 1px solid rgba(16,185,129,0.25);
//         }
//         .fu-status.error {
//           background: rgba(239,68,68,0.1); color: #fca5a5;
//           border: 1px solid rgba(239,68,68,0.2);
//         }
//       `}</style>
//     </div>
//   );
// }