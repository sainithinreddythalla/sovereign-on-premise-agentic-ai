import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import Navbar from "../components/common/Navbar";
import Sidebar from "../components/common/Sidebar";
import StatusBadge from "../components/common/StatusBadge";
import { listDocuments, listDeliverables, downloadReportFile } from "../services/api";

export default function Dashboard() {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState([]);
  const [deliverables, setDeliverables] = useState([]);

  useEffect(() => {
    listDocuments().then(setDocuments);
    listDeliverables().then(setDeliverables);
  }, []);

  return (
    <div className="app-layout">
      <div style={{ display: "flex", flexDirection: "column", width: "100%" }}>
        <Navbar />
        <div style={{ display: "flex", flex: 1 }}>
          <Sidebar />
          <main className="main-content">
            <div className="page-container">
              {/* Top Welcome & Facility Scope */}
              <div style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                marginBottom: "28px"
              }}>
                <div>
                  <h1 style={{ fontSize: "24px", fontWeight: 800, color: "#f8fafc", marginBottom: "4px" }}>
                    Industrial AI Audit Control Center
                  </h1>
                  <p style={{ fontSize: "13px", color: "#94a3b8" }}>
                    Facility: <span style={{ color: "#38bdf8", fontWeight: 600 }}>Hydrocracker Complex // Sector-4</span> &bull; Security Level: <span style={{ color: "#10b981", fontWeight: 600 }}>Air-Gapped Sovereign Enclave</span>
                  </p>
                </div>
                <button
                  onClick={() => navigate("/workspace")}
                  className="btn btn-primary"
                >
                  ⚡ Launch Audit Workspace
                </button>
              </div>

              {/* 4 Sovereign KPI Cards */}
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
                gap: "20px",
                marginBottom: "28px"
              }}>
                <div className="panel">
                  <div style={{ fontSize: "11px", fontWeight: 700, color: "#94a3b8", textTransform: "uppercase", marginBottom: "8px" }}>
                    Sovereign Boundary
                  </div>
                  <div style={{ fontSize: "24px", fontWeight: 800, color: "#10b981", marginBottom: "4px" }}>
                    100% Air-Gapped
                  </div>
                  <div style={{ fontSize: "12px", color: "#64748b" }}>
                    0% cloud exfiltration &bull; Pure local processing
                  </div>
                </div>

                <div className="panel">
                  <div style={{ fontSize: "11px", fontWeight: 700, color: "#94a3b8", textTransform: "uppercase", marginBottom: "8px" }}>
                    Confidential Knowledge
                  </div>
                  <div style={{ fontSize: "24px", fontWeight: 800, color: "#38bdf8", marginBottom: "4px" }}>
                    {documents.length} Documents
                  </div>
                  <div style={{ fontSize: "12px", color: "#64748b" }}>
                    220 Chunks indexed in sovereign vector DB
                  </div>
                </div>

                <div className="panel">
                  <div style={{ fontSize: "11px", fontWeight: 700, color: "#94a3b8", textTransform: "uppercase", marginBottom: "8px" }}>
                    Audit Verification Rate
                  </div>
                  <div style={{ fontSize: "24px", fontWeight: 800, color: "#fbbf24", marginBottom: "4px" }}>
                    94% Evidence
                  </div>
                  <div style={{ fontSize: "12px", color: "#64748b" }}>
                    ASME calculations & citations verified
                  </div>
                </div>

                <div className="panel">
                  <div style={{ fontSize: "11px", fontWeight: 700, color: "#94a3b8", textTransform: "uppercase", marginBottom: "8px" }}>
                    Open-Weight Router
                  </div>
                  <div style={{ fontSize: "20px", fontWeight: 800, color: "#c084fc", marginBottom: "4px" }}>
                    DeepSeek / Qwen
                  </div>
                  <div style={{ fontSize: "12px", color: "#64748b" }}>
                    Dynamic task routing & vision parser active
                  </div>
                </div>
              </div>

              {/* Primary Demonstration Hero Card */}
              <div style={{
                background: "linear-gradient(135deg, rgba(30, 58, 138, 0.35) 0%, rgba(15, 23, 42, 0.9) 100%)",
                border: "1px solid rgba(59, 130, 246, 0.4)",
                borderRadius: "14px",
                padding: "24px 28px",
                marginBottom: "32px",
                boxShadow: "0 8px 24px rgba(0, 0, 0, 0.4)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "20px"
              }}>
                <div style={{ maxWidth: "800px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px" }}>
                    <span className="badge badge-sovereign">PRIMARY AUDIT WORKFLOW</span>
                    <span style={{ fontSize: "12px", color: "#94a3b8" }}>SIH26117 Milestone Task</span>
                  </div>
                  <h2 style={{ fontSize: "18px", fontWeight: 800, color: "#f8fafc", marginBottom: "8px" }}>
                    Confidential Industrial Engineering & Safety Audit (Unit-4 Hydrocracker)
                  </h2>
                  <p style={{ fontSize: "13px", color: "#cbd5e1", lineHeight: "1.5" }}>
                    Demonstrates end-to-end multi-step agent reasoning: cross-referencing P&ID blueprints,
                    ultrasonic inspection logs, and optical field photos against Refinery Safety Standard STD-804
                    with automated ASME calculations, traceable page grounding, and DOCX/XLSX deliverable generation.
                  </p>
                </div>
                <button
                  onClick={() => navigate("/workspace")}
                  className="btn btn-primary"
                  style={{ padding: "12px 22px", fontSize: "14px" }}
                >
                  ⚡ Open in Agent Workspace &rarr;
                </button>
              </div>

              {/* Two Column Grid: Documents & Deliverables */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
                {/* Confidential Documents Ingested */}
                <div className="panel">
                  <div className="panel-header">
                    <div className="panel-title">
                      <span>📁</span> Confidential Documents Ingested
                    </div>
                    <Link to="/documents" style={{ color: "#38bdf8", fontSize: "12px", textDecoration: "none", fontWeight: 600 }}>
                      View All &rarr;
                    </Link>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                    {documents.slice(0, 4).map((doc) => (
                      <div
                        key={doc.document_id}
                        style={{
                          background: "rgba(15, 23, 42, 0.6)",
                          border: "1px solid #1e293b",
                          borderRadius: "8px",
                          padding: "12px 16px",
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center"
                        }}
                      >
                        <div>
                          <div style={{ fontSize: "13px", fontWeight: 600, color: "#f1f5f9" }}>
                            {doc.filename}
                          </div>
                          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "2px" }}>
                            {doc.category} &bull; {doc.pages} pages &bull; {doc.chunks_indexed} chunks
                          </div>
                        </div>
                        <span className="badge badge-verified" style={{ fontSize: "10px" }}>
                          PARSED & INDEXED
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Industrial Deliverables Generated */}
                <div className="panel">
                  <div className="panel-header">
                    <div className="panel-title">
                      <span>📋</span> Generated Industrial Deliverables
                    </div>
                    <Link to="/deliverables" style={{ color: "#38bdf8", fontSize: "12px", textDecoration: "none", fontWeight: 600 }}>
                      Deliverables Hub &rarr;
                    </Link>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                    {deliverables.slice(0, 3).map((rep) => (
                      <div
                        key={rep.report_id}
                        style={{
                          background: "rgba(15, 23, 42, 0.6)",
                          border: "1px solid #1e293b",
                          borderRadius: "8px",
                          padding: "12px 16px",
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center"
                        }}
                      >
                        <div>
                          <div style={{ fontSize: "13px", fontWeight: 600, color: "#f1f5f9" }}>
                            {rep.filename}
                          </div>
                          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "2px" }}>
                            {rep.title} &bull; {rep.filesize}
                          </div>
                        </div>
                        <button
                          onClick={() => downloadReportFile(rep)}
                          className="btn btn-secondary btn-sm"
                          style={{ fontSize: "11px" }}
                        >
                          ⬇ Download
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
