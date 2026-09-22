import React, { useState, useEffect } from "react";
import Navbar from "../components/common/Navbar";
import Sidebar from "../components/common/Sidebar";
import StatusBadge from "../components/common/StatusBadge";
import { listDeliverables, downloadReportFile } from "../services/api";

export default function Deliverables() {
  const [deliverables, setDeliverables] = useState([]);
  const [previewReport, setPreviewReport] = useState(null);

  useEffect(() => {
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
              {/* Header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
                <div>
                  <h1 style={{ fontSize: "22px", fontWeight: 800, color: "#f8fafc", marginBottom: "4px" }}>
                    Industrial Deliverables & Audit Reports
                  </h1>
                  <p style={{ fontSize: "13px", color: "#94a3b8" }}>
                    Section 17 Conformance: Verified work products generated from agentic audit findings.
                  </p>
                </div>
              </div>

              {/* Formats Overview Cards */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "20px", marginBottom: "28px" }}>
                <div className="panel" style={{ borderTop: "3px solid #3b82f6" }}>
                  <div style={{ fontSize: "26px", marginBottom: "8px" }}>📄</div>
                  <h3 style={{ fontSize: "15px", fontWeight: 700, color: "#f8fafc", marginBottom: "4px" }}>
                    Engineering Audit Report (.docx)
                  </h3>
                  <p style={{ fontSize: "12px", color: "#94a3b8", lineHeight: "1.5" }}>
                    Executive summary, code standard cross-references, ASME wall thickness calculation checks, and formal sign-off blocks.
                  </p>
                </div>

                <div className="panel" style={{ borderTop: "3px solid #10b981" }}>
                  <div style={{ fontSize: "26px", marginBottom: "8px" }}>📊</div>
                  <h3 style={{ fontSize: "15px", fontWeight: 700, color: "#f8fafc", marginBottom: "4px" }}>
                    Deviations Tracker (.xlsx)
                  </h3>
                  <p style={{ fontSize: "12px", color: "#94a3b8", lineHeight: "1.5" }}>
                    Structured spreadsheet matrix with severity rankings, exact page citations, remediation deadlines, and status tags.
                  </p>
                </div>

                <div className="panel" style={{ borderTop: "3px solid #f59e0b" }}>
                  <div style={{ fontSize: "26px", marginBottom: "8px" }}>📑</div>
                  <h3 style={{ fontSize: "15px", fontWeight: 700, color: "#f8fafc", marginBottom: "4px" }}>
                    Executive Briefing (.pptx)
                  </h3>
                  <p style={{ fontSize: "12px", color: "#94a3b8", lineHeight: "1.5" }}>
                    Slide presentation summarizing high-priority containment hazards and action plans for the plant operations committee.
                  </p>
                </div>
              </div>

              {/* Deliverables Table */}
              <div className="panel">
                <div className="panel-header">
                  <div className="panel-title">
                    <span>📋</span> Generated Deliverable Archives ({deliverables.length})
                  </div>
                  <span style={{ fontSize: "11px", color: "#38bdf8", fontWeight: 600 }}>
                    Section 11.7 Conformance
                  </span>
                </div>

                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Work Product Filename</th>
                      <th>Facility / Complex</th>
                      <th>Format</th>
                      <th>Evidence Coverage</th>
                      <th>Verification Status</th>
                      <th>Generated Timestamp</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {deliverables.map((rep) => (
                      <tr key={rep.report_id}>
                        <td>
                          <div style={{ fontWeight: 600, color: "#f1f5f9" }}>{rep.filename}</div>
                          <div style={{ fontSize: "11px", color: "#64748b" }}>{rep.title} &bull; {rep.filesize}</div>
                        </td>
                        <td>
                          <span style={{ color: "#cbd5e1", fontSize: "12px" }}>{rep.unit}</span>
                        </td>
                        <td>
                          <span className="mono" style={{
                            fontSize: "11px",
                            fontWeight: 700,
                            color: rep.format === "docx" ? "#60a5fa" : rep.format === "xlsx" ? "#34d399" : "#fbbf24",
                            background: "rgba(15, 23, 42, 0.8)",
                            padding: "3px 8px",
                            borderRadius: "4px",
                            border: "1px solid #1e293b"
                          }}>
                            {rep.format.toUpperCase()}
                          </span>
                        </td>
                        <td className="mono" style={{ color: "#38bdf8", fontWeight: 700 }}>
                          {rep.evidence_coverage}
                        </td>
                        <td>
                          <StatusBadge type="verification" value="verified_with_evidence" />
                        </td>
                        <td style={{ fontSize: "12px", color: "#94a3b8" }}>
                          {rep.generated_at}
                        </td>
                        <td>
                          <div style={{ display: "flex", gap: "8px" }}>
                            <button
                              onClick={() => setPreviewReport(rep)}
                              className="btn btn-secondary btn-sm"
                              style={{ fontSize: "11px", padding: "4px 8px" }}
                            >
                              Inspect
                            </button>
                            <button
                              onClick={() => downloadReportFile(rep)}
                              className="btn btn-primary btn-sm"
                              style={{ fontSize: "11px", padding: "4px 10px" }}
                            >
                              ⬇ Export
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* In-Browser Report Preview Modal */}
              {previewReport && (
                <div style={{
                  position: "fixed",
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: "rgba(0, 0, 0, 0.8)",
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
                    width: "750px",
                    maxWidth: "100%",
                    maxHeight: "85vh",
                    display: "flex",
                    flexDirection: "column",
                    boxShadow: "0 25px 50px rgba(0, 0, 0, 0.7)"
                  }}>
                    <div style={{
                      padding: "20px 24px",
                      borderBottom: "1px solid #1e293b",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center"
                    }}>
                      <div>
                        <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#f8fafc" }}>
                          {previewReport.filename}
                        </h3>
                        <span style={{ fontSize: "11px", color: "#94a3b8" }}>
                          Sovereign Deliverable Preview &bull; {previewReport.unit}
                        </span>
                      </div>
                      <button
                        onClick={() => setPreviewReport(null)}
                        className="btn btn-secondary btn-sm"
                      >
                        ✕ Close
                      </button>
                    </div>

                    <div style={{
                      padding: "20px 24px",
                      overflowY: "auto",
                      flex: 1
                    }}>
                      <pre style={{
                        background: "#080c14",
                        border: "1px solid #1e293b",
                        borderRadius: "8px",
                        padding: "16px",
                        fontFamily: "var(--font-mono)",
                        fontSize: "12px",
                        color: "#cbd5e1",
                        lineHeight: "1.5",
                        whiteSpace: "pre-wrap",
                        wordBreak: "break-word"
                      }}>
{`================================================================================
SIH26117 — SOVEREIGN INDUSTRIAL AI WORKBENCH
CONFIDENTIAL ENGINEERING & SAFETY AUDIT REPORT
================================================================================
Facility / Unit: Hydrocracker Complex // Unit-4
Document ID: ${previewReport.report_id}
Generated: ${previewReport.generated_at}
Classification: RESTRICTED // ON-PREMISE AIR-GAPPED SYSTEM
Evidence Coverage: 94%
Verification Status: VERIFIED WITH EVIDENCE (Requires Operational Sign-Off)

EXECUTIVE SUMMARY
--------------------------------------------------------------------------------
An automated sovereign multi-model agentic audit was conducted on Unit-4 
Reactor Feed Drum V-401, associated Relief Valve PSV-401, and line 04-P-201 
against Refinery Safety Standard STD-804.

Three (3) non-conformances were detected and verified:

1. [CRITICAL] Shell Wall Thickness Degradation (ASME Sec VIII Div 1 Deficit)
   - Code Standard: Refinery_Safety_Standard_STD-804.pdf (Page 17, §5.1)
     Requires minimum 12.50 mm (inclusive of 3.0 mm corrosion allowance).
   - Observed Data: Pressure_Vessel_V401_Inspection_Report.pdf (Page 4, §3.2)
     Actual measured thickness is 11.20 mm (Deficit: 1.30 mm / 10.4%).
   - Action: Immediately de-rate operating pressure to 1.95 MPa maximum.

2. [HIGH] Overdue Relief Valve (PSV-401) Bench Recalibration
   - Code Standard: Refinery_Safety_Standard_STD-804.pdf (Page 9, §4.2)
     Maximum permissible test interval is 12 months in sour service.
   - Observed Data: Pressure_Vessel_V401_Inspection_Report.pdf (Page 8, §6.1)
     Last test date stamped: 2024-11-12 (22 months elapsed).
   - Action: Replace with certified spare within 48 hours.

3. [MEDIUM] Emergency Depressuring Bypass Valve in Unauthorized State
   - Code Standard: Refinery_Safety_Standard_STD-804.pdf (Page 22, §6.3)
     Must remain chained and locked CLOSED (Car-Seal Closed).
   - Observed Data: Hydrocracker_Unit4_PID_DWG-401.pdf (Page 1, Grid C-2)
     Line 04-P-201-CS shows valve HV-401B labeled 'Normally Open (NO)'.
   - Action: Conduct physical field Lock-Out/Tag-Out check and verify MOC register.

VERIFICATION STAMP & SIGN-OFF
--------------------------------------------------------------------------------
Grounding Verification: PASS (Calculated Coverage: 0.94)
ASME Sec VIII Calculation Check: VERIFIED
Lead Auditor Sign-Off: Nithin (Lead Auditor)       Date: 2026-09-06
================================================================================`}
                      </pre>
                    </div>

                    <div style={{
                      padding: "16px 24px",
                      borderTop: "1px solid #1e293b",
                      display: "flex",
                      justifyContent: "flex-end",
                      gap: "10px"
                    }}>
                      <button
                        onClick={() => downloadReportFile(previewReport)}
                        className="btn btn-primary btn-sm"
                      >
                        ⬇ Download Formal File ({previewReport.format.toUpperCase()})
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
