// import axios from "axios";

// const API = axios.create({
//   baseURL: "http://localhost:8000"
// });

// export const uploadStructured = (file) => {
//   const form = new FormData();
//   form.append("file", file);

//   return API.post("/upload/structured", form, {
//     headers: { "Content-Type": "multipart/form-data" }
//   });
// };

// export const uploadDocument = (file) => {
//   const form = new FormData();
//   form.append("file", file);

//   return API.post("/upload/document", form, {
//     headers: { "Content-Type": "multipart/form-data" }
//   });
// };

// export const getStructured = () =>
//   API.get("/upload/list/structured");

// export const getDocuments = () =>
//   API.get("/upload/list/documents");

// // ✅ FIXED: clean payload
// export const sendQuery = (payload) =>
//   API.post("/query/", payload);

import axios from "axios";

const API = axios.create({ baseURL: "http://localhost:8000" });

// ── File Uploads ───────────────────────────────────────────────────
export const uploadStructured = (file) => {
  const form = new FormData();
  form.append("file", file);
  return API.post("/upload/structured", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const uploadDocument = (file) => {
  const form = new FormData();
  form.append("file", file);
  return API.post("/upload/document", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};
export const getDocumentStatus = (documentId) =>
  API.get(`/upload/list/documents`).then((res) => {
    const doc = res.data.find((d) => d.id === documentId);
    return doc?.is_indexed ?? 0;   // 0 = processing, 1 = ready, 2 = error
  });
// ── Live Data Sources ──────────────────────────────────────────────
export const connectGoogleSheets = (url, sheet_name = null) =>
  API.post("/upload/google-sheets", { url, sheet_name });

export const connectDatabase = (connection_string, table_name, query = null) =>
  API.post("/upload/database", { connection_string, table_name, query });

// ── Query ──────────────────────────────────────────────────────────
export const sendQuery = ({ query, data_source_id = null, document_id = null }) =>
  API.post("/query/", { query, data_source_id, document_id });