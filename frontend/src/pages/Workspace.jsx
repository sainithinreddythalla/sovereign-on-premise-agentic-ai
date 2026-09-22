import React, { useState, useEffect } from "react";
import Navbar from "../components/common/Navbar";
import Sidebar from "../components/common/Sidebar";
import StatusBadge from "../components/common/StatusBadge";
import {
  listDocuments,
  createTask,
  getTaskStatus,
  generateReport,
  downloadReportFile
} from "../services/api";
import { AUDIT_PRESETS, MOCK_TASK_EXECUTION } from "../services/mockData";

export default function Workspace() {
  const [documents, setDocuments] = useState([]);
  const [selectedPreset, setSelectedPreset] = useState("preset_hydrocracker_audit");
  const [taskPrompt, setTaskPrompt] = useState(AUDIT_PRESETS[0].prompt);
  const [selectedDocIds, setSelectedDocIds] = useState(AUDIT_PRESETS[0].document_ids);
  const [selectedModel, setSelectedModel] = useState("Auto (Intelligent Sovereign Router)");

  // Agent execution state
  const [isRunning, setIsRunning] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(6); // default to finished view for immediate inspection
  const [taskData, setTaskData] = useState(MOCK_TASK_EXECUTION);
  const [showConsole, setShowConsole] = useState(true);
  const [activeTab, setActiveTab] = useState("findings"); // findings | sources | deliverables

  useEffect(() => {
    listDocuments().then(setDocuments);
  }, []);

  const handleSelectPreset = (presetId) => {
    const preset = AUDIT_PRESETS.find((p) => p.id === presetId);
    if (preset) {
      setSelectedPreset(preset.id);
      setTaskPrompt(preset.prompt);
      setSelectedDocIds(preset.document_ids);
      setSelectedModel(preset.preferred_model);
    }
  };

  const handleToggleDoc = (docId) => {
    setSelectedDocIds((prev) =>
      prev.includes(docId) ? prev.filter((id) => id !== docId) : [...prev, docId]
    );
  };

  // Live simulation of agent execution stepper
  const handleExecuteAudit = async () => {
    setIsRunning(true);
    setCurrentStepIndex(0);
    setActiveTab("findings");

    await createTask({
      message: taskPrompt,
      document_ids: selectedDocIds,
      preferred_model: selectedModel
    });

    // Step-by-step progression with realistic timing
    const stepDelays = [400, 700, 900, 1100, 900, 800, 500];
    for (let i = 0; i < stepDelays.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, stepDelays[i]));
      setCurrentStepIndex(i);
    }

    const completedTask = await getTaskStatus("task_hc_demo_001");
    setTaskData(completedTask);
    setIsRunning(false);
  };

  const handleDownloadDeliverable = (format) => {
    const filename = `Unit4_Hydrocracker_Audit_${Date.now().toString().slice(-4)}.${format}`;
    downloadReportFile({
      report_id: `rep_${Date.now().toString().slice(-4)}`,
      filename,
      format,
      title: "Confidential Industrial Engineering & Safety Audit Report"
    });
  };

  const currentStep = taskData.execution_steps[currentStepIndex] || taskData.execution_steps[6];
  const isAuditDone = currentStepIndex === 6 && !isRunning;

  return (
    <div className="app-layout">
      <div style={{ display: "flex", flexDirection: "column", width: "100%" }}>
        <Navbar />
        <div style={{ display: "flex", flex: 1 }}>
          <Sidebar />
          <main className="main-content">
            <div className="page-container">
              {/* Workspace Header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
                <div>
                  <h1 style={{ fontSize: "22px", fontWeight: 800, color: "#f8fafc", marginBottom: "4px" }}>
                    Sovereign AI Audit Workspace
                  </h1>
                  <p style={{ fontSize: "13px", color: "#94a3b8" }}>
                    Multi-step agent planning, tool-grounded reasoning, mathematical verification, and deliverable assembly.
                  </p>
                </div>

                <div style={{ display: "flex", gap: "10px" }}>
                  <button
                    onClick={() => handleExecuteAudit()}
                    disabled={isRunning || selectedDocIds.length === 0}
                    className="btn btn-primary"
                    style={{ minWidth: "190px" }}
                  >
                    {isRunning ? (
                      <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <span className="pulse-active" style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#38bdf8" }} />
                        Auditing ({currentStep.phase})...
                      </span>
                    ) : (
                      "⚡ Execute Industrial Audit"
                    )}
                  </button>
                </div>
              </div>

              {/* Two Column Layout: Setup vs Execution */}
              <div style={{ display: "grid", gridTemplateColumns: "380px 1fr", gap: "24px", alignItems: "start" }}>
                
                {/* Left Panel: Audit Goal & Document Selection */}
                <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                  {/* Preset Audit Selector */}
                  <div className="panel">
                    <div className="panel-title" style={{ marginBottom: "12px" }}>
                      <span>🎯</span> Industrial Audit Preset
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                      {AUDIT_PRESETS.map((preset) => (
                        <button
                          key={preset.id}
                          type="button"
                          onClick={() => handleSelectPreset(preset.id)}
                          style={{
                            textAlign: "left",
                            padding: "10px 14px",
                            borderRadius: "8px",
                            background: selectedPreset === preset.id ? "rgba(37, 99, 235, 0.25)" : "var(--bg-surface)",
                            border: `1px solid ${selectedPreset === preset.id ? "rgba(59, 130, 246, 0.6)" : "var(--border-subtle)"}`,
                            color: selectedPreset === preset.id ? "#ffffff" : "#cbd5e1",
                            cursor: "pointer",
                            fontSize: "12px",
                            fontWeight: selectedPreset === preset.id ? 700 : 500,
                            transition: "all 0.15s"
                          }}
                        >
                          {preset.name}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Task Prompt Input */}
                  <div className="panel">
                    <div className="panel-title" style={{ marginBottom: "12px" }}>
                      <span>📝</span> Audit Objective / Prompt
                    </div>
                    <textarea
                      className="input-field"
                      rows={4}
                      value={taskPrompt}
                      onChange={(e) => setTaskPrompt(e.target.value)}
                      placeholder="Specify industrial audit requirements..."
                      style={{ fontSize: "13px", lineHeight: "1.4" }}
                    />
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "8px" }}>
                      <span style={{ fontSize: "11px", color: "#64748b" }}>Section 11.3 Task Contract</span>
                      <span style={{ fontSize: "11px", color: "#38bdf8" }}>Grounded Multi-Step</span>
                    </div>
                  </div>

                  {/* Document Scope Multi-Select */}
                  <div className="panel">
                    <div className="panel-header" style={{ marginBottom: "12px", paddingBottom: "8px" }}>
                      <div className="panel-title" style={{ fontSize: "14px" }}>
                        <span>📂</span> Audit Documents Scope
                      </div>
                      <span style={{ fontSize: "11px", color: "#94a3b8" }}>
                        {selectedDocIds.length} of {documents.length} Selected
                      </span>
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                      {documents.map((doc) => {
                        const isSelected = selectedDocIds.includes(doc.document_id);
                        return (
                          <div
                            key={doc.document_id}
                            onClick={() => handleToggleDoc(doc.document_id)}
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: "10px",
                              padding: "9px 12px",
                              borderRadius: "6px",
                              background: isSelected ? "rgba(30, 41, 59, 0.7)" : "rgba(15, 23, 42, 0.4)",
                              border: `1px solid ${isSelected ? "rgba(56, 189, 248, 0.4)" : "var(--border-subtle)"}`,
                              cursor: "pointer",
                              userSelect: "none"
                            }}
                          >
                            <input
                              type="checkbox"
                              checked={isSelected}
                              onChange={() => {}}
                              style={{ cursor: "pointer", accentColor: "#2563eb" }}
                            />
                            <div style={{ flex: 1, minWidth: 0 }}>
                              <div style={{
                                fontSize: "12px",
                                fontWeight: 600,
                                color: isSelected ? "#f1f5f9" : "#94a3b8",
                                whiteSpace: "nowrap",
                                overflow: "hidden",
                                textOverflow: "ellipsis"
                              }}>
                                {doc.filename}
                              </div>
                              <div style={{ fontSize: "10px", color: "#64748b" }}>
                                {doc.category} ({doc.pages}p)
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Model Router Selector */}
                  <div className="panel">
                    <div className="panel-title" style={{ marginBottom: "10px", fontSize: "14px" }}>
                      <span>🤖</span> Sovereign AI Model Router
                    </div>
                    <select
                      className="input-field"
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      style={{ fontSize: "12px" }}
                    >
                      <option value="Auto (Intelligent Sovereign Router)">Auto: Dynamic Task Routing</option>
                      <option value="DeepSeek-R1 (Local Reasoning)">DeepSeek-R1 (Local Reasoning Engine)</option>
                      <option value="Qwen-2.5-Coder (Engineering Math)">Qwen-2.5-Coder (Engineering Math & Logic)</option>
                      <option value="Qwen-VL / Llava (Multimodal Vision)">Qwen-VL / Llava (Multimodal P&ID Vision)</option>
                    </select>
                  </div>
                </div>

                {/* Right Panel: Stepper, Live Console & Findings Matrix */}
                <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                  
                  {/* 7-Stage Live Agent Stepper */}
                  <div className="panel" style={{ padding: "18px 24px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                      <div style={{ fontSize: "13px", fontWeight: 700, color: "#f8fafc", display: "flex", alignItems: "center", gap: "8px" }}>
                        <span>⚡</span> AGENT EXECUTION PIPELINE (7 PHASES)
                      </div>
                      <div style={{ fontSize: "12px", color: "#94a3b8" }}>
                        Status: <strong style={{ color: isAuditDone ? "#10b981" : "#38bdf8" }}>{currentStep.phase.toUpperCase()}</strong>
                      </div>
                    </div>

                    <div style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      position: "relative",
                      margin: "12px 0 16px 0"
                    }}>
                      {/* Connecting Background Line */}
                      <div style={{
                        position: "absolute",
                        top: "16px",
                        left: "24px",
                        right: "24px",
                        height: "2px",
                        background: "#1e293b",
                        zIndex: 0
                      }} />

                      {taskData.execution_steps.map((step, idx) => {
                        const isDone = idx < currentStepIndex || isAuditDone;
                        const isCurrent = idx === currentStepIndex && isRunning;
                        return (
                          <div
                            key={step.phase}
                            style={{
                              display: "flex",
                              flexDirection: "column",
                              alignItems: "center",
                              position: "relative",
                              zIndex: 1
                            }}
                          >
                            <div style={{
                              width: "32px",
                              height: "32px",
                              borderRadius: "50%",
                              background: isDone ? "#059669" : isCurrent ? "#2563eb" : "#0f172a",
                              border: `2px solid ${isDone ? "#10b981" : isCurrent ? "#38bdf8" : "#334155"}`,
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              fontSize: "12px",
                              fontWeight: 700,
                              color: isDone || isCurrent ? "white" : "#64748b",
                              boxShadow: isCurrent ? "0 0 12px rgba(56, 189, 248, 0.6)" : "none",
                              transition: "all 0.3s"
                            }}>
                              {isDone ? "✓" : idx + 1}
                            </div>
                            <span style={{
                              fontSize: "10px",
                              fontWeight: 600,
                              marginTop: "6px",
                              textTransform: "uppercase",
                              color: isDone ? "#34d399" : isCurrent ? "#38bdf8" : "#64748b"
                            }}>
                              {step.phase}
                            </span>
                          </div>
                        );
                      })}
                    </div>

                    {/* Current Stage Status Callout */}
                    <div style={{
                      background: "rgba(15, 23, 42, 0.8)",
                      border: "1px solid #1e293b",
                      borderRadius: "8px",
                      padding: "10px 14px",
                      fontSize: "12px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between"
                    }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                        <span style={{ color: "#38bdf8", fontWeight: 700 }}>Stage {currentStepIndex + 1}/7:</span>
                        <span style={{ color: "#e2e8f0" }}>{currentStep.label} &mdash; {currentStep.detail}</span>
                      </div>
                      <span className="mono" style={{ fontSize: "11px", color: "#64748b" }}>
                        {currentStep.timestamp}
                      </span>
                    </div>
                  </div>

                  {/* Collapsible Controlled Tools Console */}
                  <div className="panel" style={{ padding: "14px 18px" }}>
                    <div
                      onClick={() => setShowConsole(!showConsole)}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        cursor: "pointer",
                        userSelect: "none"
                      }}
                    >
                      <div style={{ fontSize: "12px", fontWeight: 700, color: "#94a3b8", display: "flex", alignItems: "center", gap: "8px" }}>
                        <span>🖥️</span> CONTROLLED TOOL EXECUTION AUDIT LOG
                      </div>
                      <span style={{ fontSize: "11px", color: "#38bdf8" }}>
                        {showConsole ? "Hide Console ▲" : "Show Console ▼"}
                      </span>
                    </div>

                    {showConsole && (
                      <div style={{
                        marginTop: "12px",
                        background: "#080c14",
                        border: "1px solid #1e293b",
                        borderRadius: "8px",
                        padding: "12px 14px",
                        fontFamily: "var(--font-mono)",
                        fontSize: "11px",
                        lineHeight: "1.6",
                        color: "#94a3b8",
                        maxHeight: "160px",
                        overflowY: "auto"
                      }}>
                        <div><span style={{ color: "#10b981" }}>[10:00:01]</span> <span style={{ color: "#38bdf8" }}>SOVEREIGN_SANDBOX:</span> Verified 0 network outbound sockets. All operations locked to localhost.</div>
                        <div><span style={{ color: "#10b981" }}>[10:00:03]</span> <span style={{ color: "#a855f7" }}>MODEL_ROUTER:</span> Selected DeepSeek-R1 for safety analysis & Qwen-VL for P&ID optical symbols.</div>
                        <div><span style={{ color: "#10b981" }}>[10:00:07]</span> <span style={{ color: "#fbbf24" }}>TOOL CALL:</span> rag_search(query="STD-804 shell thickness relief valve intervals", top_k=8) &rarr; 8 chunks (avg score: 0.94)</div>
                        <div><span style={{ color: "#10b981" }}>[10:00:12]</span> <span style={{ color: "#fbbf24" }}>TOOL CALL:</span> engineering_calc(type="asme_wall_thickness", P=2.4MPa, R=600mm, S=118MPa, E=0.85, CA=3.0mm) &rarr; t_min=12.50mm</div>
                        <div><span style={{ color: "#10b981" }}>[10:00:16]</span> <span style={{ color: "#fbbf24" }}>TOOL CALL:</span> vision_inspection(target="PSV-401 flange", doc_id="doc_004") &rarr; Flange galvanic corrosion confirmed, lead seal broken</div>
                        <div><span style={{ color: "#10b981" }}>[10:00:19]</span> <span style={{ color: "#10b981" }}>VERIFIER:</span> Evidence grounding check passed (0.94 score). 1 item flagged for physical engineer review.</div>
                        <div><span style={{ color: "#10b981" }}>[10:00:21]</span> <span style={{ color: "#38bdf8" }}>DELIVERABLE_ENGINE:</span> Compiled DOCX, XLSX, and PPTX reports.</div>
                      </div>
                    )}
                  </div>

                  {/* Findings, Sources & Deliverables Navigation Bar */}
                  <div style={{ display: "flex", gap: "10px", borderBottom: "1px solid #1e293b", paddingBottom: "10px" }}>
                    <button
                      onClick={() => setActiveTab("findings")}
                      className={`btn ${activeTab === "findings" ? "btn-primary" : "btn-secondary"} btn-sm`}
                    >
                      Audit Findings ({taskData.findings.length})
                    </button>
                    <button
                      onClick={() => setActiveTab("sources")}
                      className={`btn ${activeTab === "sources" ? "btn-primary" : "btn-secondary"} btn-sm`}
                    >
                      Grounded Sources ({taskData.sources.length})
                    </button>
                    <button
                      onClick={() => setActiveTab("deliverables")}
                      className={`btn ${activeTab === "deliverables" ? "btn-primary" : "btn-secondary"} btn-sm`}
                    >
                      Generated Deliverables (3)
                    </button>
                  </div>

                  {/* TAB 1: Audit Findings Matrix */}
                  {activeTab === "findings" && (
                    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                      {taskData.findings.map((fnd) => (
                        <div key={fnd.finding_id} className="panel" style={{ borderLeft: `4px solid ${fnd.severity === "critical" ? "#ef4444" : fnd.severity === "high" ? "#f59e0b" : "#3b82f6"}` }}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                            <div>
                              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                                <span className="mono" style={{ fontSize: "11px", fontWeight: 700, color: "#94a3b8" }}>
                                  {fnd.finding_id}
                                </span>
                                <StatusBadge type="severity" value={fnd.severity} />
                                <StatusBadge type="verification" value={fnd.verification_status} />
                              </div>
                              <h3 style={{ fontSize: "15px", fontWeight: 700, color: "#f8fafc" }}>
                                {fnd.title}
                              </h3>
                            </div>
                            <span style={{ fontSize: "11px", color: "#64748b" }}>{fnd.category}</span>
                          </div>

                          {/* Side-by-Side Requirement vs Observed Evidence Matrix */}
                          <div style={{
                            display: "grid",
                            gridTemplateColumns: "1fr 1fr",
                            gap: "14px",
                            background: "rgba(15, 23, 42, 0.6)",
                            border: "1px solid #1e293b",
                            borderRadius: "8px",
                            padding: "14px",
                            marginBottom: "14px"
                          }}>
                            {/* Left: Code Standard Requirement */}
                            <div>
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                                <span style={{ fontSize: "11px", fontWeight: 700, color: "#38bdf8", textTransform: "uppercase" }}>
                                  📜 Mandatory Code Requirement
                                </span>
                                <span className="badge badge-sovereign" style={{ fontSize: "9px" }}>
                                  {fnd.requirement_source.filename} &bull; Page {fnd.requirement_source.page}
                                </span>
                              </div>
                              <div style={{ fontSize: "11px", color: "#94a3b8", fontWeight: 600, marginBottom: "4px" }}>
                                {fnd.requirement_source.section}
                              </div>
                              <p style={{ fontSize: "12px", color: "#cbd5e1", fontStyle: "italic", background: "rgba(0,0,0,0.2)", padding: "8px", borderRadius: "6px" }}>
                                &ldquo;{fnd.requirement_text}&rdquo;
                              </p>
                            </div>

                            {/* Right: Observed Field Inspection Evidence */}
                            <div>
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                                <span style={{ fontSize: "11px", fontWeight: 700, color: "#fbbf24", textTransform: "uppercase" }}>
                                  🔍 Observed Field Evidence
                                </span>
                                <span className="badge badge-review" style={{ fontSize: "9px" }}>
                                  {fnd.observed_source.filename} &bull; Page {fnd.observed_source.page}
                                </span>
                              </div>
                              <div style={{ fontSize: "11px", color: "#94a3b8", fontWeight: 600, marginBottom: "4px" }}>
                                {fnd.observed_source.section}
                              </div>
                              <p style={{ fontSize: "12px", color: "#cbd5e1", fontStyle: "italic", background: "rgba(0,0,0,0.2)", padding: "8px", borderRadius: "6px" }}>
                                &ldquo;{fnd.observed_text}&rdquo;
                              </p>
                            </div>
                          </div>

                          {/* Verification Notes & Formula Details */}
                          <div style={{
                            fontSize: "12px",
                            color: "#94a3b8",
                            background: "rgba(16, 185, 129, 0.08)",
                            border: "1px solid rgba(16, 185, 129, 0.25)",
                            borderRadius: "6px",
                            padding: "8px 12px",
                            marginBottom: "10px"
                          }}>
                            <strong style={{ color: "#34d399" }}>Verification Layer: </strong>
                            {fnd.verification_notes}
                          </div>

                          {/* Remediation Recommendation */}
                          <div style={{ fontSize: "12px", color: "#f1f5f9" }}>
                            <strong style={{ color: "#f87171" }}>Required Engineering Action: </strong>
                            {fnd.recommendation}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* TAB 2: Grounded Sources */}
                  {activeTab === "sources" && (
                    <div className="panel">
                      <div className="panel-title" style={{ marginBottom: "14px" }}>
                        <span>📚</span> Traceable Document Citations ({taskData.sources.length})
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                        {taskData.sources.map((src, i) => (
                          <div
                            key={i}
                            style={{
                              background: "rgba(15, 23, 42, 0.7)",
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
                                {src.filename}
                              </div>
                              <div style={{ fontSize: "12px", color: "#94a3b8", marginTop: "2px" }}>
                                {src.reference}
                              </div>
                            </div>
                            <span className="badge badge-sovereign" style={{ fontSize: "11px" }}>
                              PAGE {src.page}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* TAB 3: Deliverables & Downloads */}
                  {activeTab === "deliverables" && (
                    <div className="panel">
                      <div className="panel-title" style={{ marginBottom: "14px" }}>
                        <span>📋</span> Audit Work Products Ready for Export
                      </div>
                      <p style={{ fontSize: "13px", color: "#94a3b8", marginBottom: "16px" }}>
                        Section 17 Conformance: The workbench produces genuine work products (formal audit report, compliance matrix, and briefing slides).
                      </p>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px" }}>
                        <div style={{ background: "rgba(15, 23, 42, 0.7)", border: "1px solid #1e293b", borderRadius: "10px", padding: "18px", textAlign: "center" }}>
                          <div style={{ fontSize: "28px", marginBottom: "8px" }}>📄</div>
                          <div style={{ fontSize: "14px", fontWeight: 700, color: "#f8fafc", marginBottom: "4px" }}>DOCX Audit Report</div>
                          <div style={{ fontSize: "11px", color: "#64748b", marginBottom: "14px" }}>Full formal report with signatures & stamps</div>
                          <button onClick={() => handleDownloadDeliverable("docx")} className="btn btn-primary btn-sm" style={{ width: "100%" }}>
                            ⬇ Download DOCX
                          </button>
                        </div>

                        <div style={{ background: "rgba(15, 23, 42, 0.7)", border: "1px solid #1e293b", borderRadius: "10px", padding: "18px", textAlign: "center" }}>
                          <div style={{ fontSize: "28px", marginBottom: "8px" }}>📊</div>
                          <div style={{ fontSize: "14px", fontWeight: 700, color: "#f8fafc", marginBottom: "4px" }}>XLSX Matrix</div>
                          <div style={{ fontSize: "11px", color: "#64748b", marginBottom: "14px" }}>Machine-readable deviation register</div>
                          <button onClick={() => handleDownloadDeliverable("xlsx")} className="btn btn-primary btn-sm" style={{ width: "100%" }}>
                            ⬇ Download XLSX
                          </button>
                        </div>

                        <div style={{ background: "rgba(15, 23, 42, 0.7)", border: "1px solid #1e293b", borderRadius: "10px", padding: "18px", textAlign: "center" }}>
                          <div style={{ fontSize: "28px", marginBottom: "8px" }}>📑</div>
                          <div style={{ fontSize: "14px", fontWeight: 700, color: "#f8fafc", marginBottom: "4px" }}>PPTX Deck</div>
                          <div style={{ fontSize: "11px", color: "#64748b", marginBottom: "14px" }}>Executive slide presentation</div>
                          <button onClick={() => handleDownloadDeliverable("pptx")} className="btn btn-primary btn-sm" style={{ width: "100%" }}>
                            ⬇ Download PPTX
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                </div>

              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
