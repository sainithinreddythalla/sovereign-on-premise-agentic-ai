import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/common/Navbar";
import Sidebar from "../components/common/Sidebar";
import { listDocuments, uploadDocument } from "../services/api";

export default function Documents() {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  useEffect(() => {
    loadDocs();
  }, []);

  const loadDocs = () => {
    listDocuments().then(setDocuments);
  };

  const handleFileUpload = async (file) => {
    if (!file) return;
    setIsUploading(true);
    await uploadDocument(file);
    setIsUploading(false);
    loadDocs();
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="app-layout">
      <div style={{ display: "flex", flexDirection: "column", width: "100%" }}>
        <Navbar />
        <div style={{ display: "flex", flex: 1 }}>
          <Sidebar />
          <main className="main-content">
            <div className="page-container">
              {/* Header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
                <div>
                  <h1 style={{ fontSize: "22px", fontWeight: 800, color: "#f8fafc", marginBottom: "4px" }}>
                    Confidential Document Repository
                  </h1>
                  <p style={{ fontSize: "13px", color: "#94a3b8" }}>
                    Air-gapped document ingestion: automatic text extraction, OCR, page chunking, and sovereign vector indexing.
                  </p>
                </div>
                <button
                  onClick={() => navigate("/workspace")}
                  className="btn btn-primary"
                >
                  ⚡ Start Audit with These Documents
                </button>
              </div>

              {/* Drag and Drop Ingestion Box */}
              <div
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={onDrop}
                style={{
                  border: `2px dashed ${dragOver ? "#38bdf8" : "#1e293b"}`,
                  borderRadius: "12px",
                  background: dragOver ? "rgba(56, 189, 248, 0.05)" : "rgba(15, 23, 42, 0.6)",
                  padding: "32px",
                  textAlign: "center",
                  marginBottom: "28px",
                  transition: "all 0.2s"
                }}
              >
                <div style={{ fontSize: "36px", marginBottom: "12px" }}>📁</div>
                <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#f8fafc", marginBottom: "6px" }}>
                  Upload Confidential Industrial Documents
                </h3>
                <p style={{ fontSize: "13px", color: "#94a3b8", marginBottom: "16px" }}>
                  Supports Engineering Drawings (P&ID), Safety Manuals (PDF), NDT Inspection Logs, and Optical Equipment Photos.
                </p>
                
                <label className="btn btn-secondary" style={{ cursor: "pointer", display: "inline-flex" }}>
                  <span>{isUploading ? "Ingesting & Indexing..." : "Browse Local File System"}</span>
                  <input
                    type="file"
                    style={{ display: "none" }}
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        handleFileUpload(e.target.files[0]);
                      }
                    }}
                  />
                </label>

                <div style={{ marginTop: "14px", fontSize: "11px", color: "#64748b" }}>
                  🔒 Documents never leave this device. Encrypted and indexed into local vector database.
                </div>
              </div>

              {/* Documents Table */}
              <div className="panel">
                <div className="panel-header">
                  <div className="panel-title">
                    <span>📑</span> Ingested Documents ({documents.length})
                  </div>
                  <span style={{ fontSize: "11px", color: "#38bdf8", fontWeight: 600 }}>
                    Section 11.1 & 11.2 Conformance
                  </span>
                </div>

                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Document Filename</th>
                      <th>Category</th>
                      <th>Pages</th>
                      <th>Chunks</th>
                      <th>Security Classification</th>
                      <th>Parsing Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map((doc) => (
                      <tr key={doc.document_id}>
                        <td>
                          <div style={{ fontWeight: 600, color: "#f1f5f9" }}>{doc.filename}</div>
                          <div style={{ fontSize: "11px", color: "#64748b" }}>{doc.filesize} &bull; {doc.upload_date}</div>
                        </td>
                        <td>
                          <span style={{ color: "#cbd5e1" }}>{doc.category}</span>
                        </td>
                        <td className="mono" style={{ color: "#38bdf8" }}>{doc.pages}</td>
                        <td className="mono" style={{ color: "#94a3b8" }}>{doc.chunks_indexed}</td>
                        <td>
                          <span className="badge badge-sovereign" style={{ fontSize: "9px" }}>
                            {doc.security_tag}
                          </span>
                        </td>
                        <td>
                          <span className="badge badge-verified" style={{ fontSize: "9px" }}>
                            ✓ {doc.status.toUpperCase()}
                          </span>
                        </td>
                        <td>
                          <button
                            onClick={() => setSelectedDoc(doc)}
                            className="btn btn-secondary btn-sm"
                            style={{ fontSize: "11px", padding: "4px 8px" }}
                          >
                            Inspect Excerpt
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Excerpt Modal */}
              {selectedDoc && (
                <div style={{
                  position: "fixed",
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: "rgba(0, 0, 0, 0.75)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  zIndex: 100,
                  padding: "20px"
                }}>
                  <div style={{
                    background: "#0f172a",
                    border: "1px solid #1e293b",
                    borderRadius: "14px",
                    width: "650px",
                    maxWidth: "100%",
                    padding: "24px",
                    boxShadow: "0 25px 50px rgba(0, 0, 0, 0.7)"
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                      <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#f8fafc" }}>
                        {selectedDoc.filename}
                      </h3>
                      <button
                        onClick={() => setSelectedDoc(null)}
                        className="btn btn-secondary btn-sm"
                      >
                        ✕ Close
                      </button>
                    </div>

                    <div style={{ display: "flex", gap: "10px", marginBottom: "16px" }}>
                      <span className="badge badge-sovereign">{selectedDoc.category}</span>
                      <span className="badge badge-verified">{selectedDoc.pages} Pages Indexed</span>
                      <span className="badge badge-sovereign">{selectedDoc.chunks_indexed} Chunks in Vector DB</span>
                    </div>

                    <div style={{
                      background: "#080c14",
                      border: "1px solid #1e293b",
                      borderRadius: "8px",
                      padding: "16px",
                      color: "#cbd5e1",
                      fontSize: "13px",
                      lineHeight: "1.6",
                      marginBottom: "20px"
                    }}>
                      <div style={{ fontWeight: 700, color: "#38bdf8", marginBottom: "6px" }}>Extracted Document Abstract:</div>
                      {selectedDoc.summary}
                    </div>

                    <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
                      <button
                        onClick={() => {
                          setSelectedDoc(null);
                          navigate("/workspace");
                        }}
                        className="btn btn-primary btn-sm"
                      >
                        ⚡ Audit This Document in Workspace
                      </button>
                    </div>
                  </div>
                </div>
              )}

            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
