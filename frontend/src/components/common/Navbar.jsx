import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { checkBackendHealth, getSimulatorMode, setSimulatorMode } from "../../services/api";

export default function Navbar() {
  const navigate = useNavigate();
  const [isSimulator, setIsSimulator] = useState(getSimulatorMode());
  const [backendStatus, setBackendStatus] = useState("Checking...");

  useEffect(() => {
    checkBackendHealth().then((status) => {
      setBackendStatus(status.mode);
      setIsSimulator(getSimulatorMode());
    });
  }, []);

  const handleToggleMode = () => {
    const nextMode = !isSimulator;
    setSimulatorMode(nextMode);
    setIsSimulator(nextMode);
    setBackendStatus(nextMode ? "Sovereign Local Simulator" : "Live Backend");
  };

  const handleSignOut = () => {
    navigate("/");
  };

  return (
    <header style={{
      height: "64px",
      background: "#0d1322",
      borderBottom: "1px solid #1e293b",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "0 28px",
      position: "sticky",
      top: 0,
      zIndex: 50
    }}>
      {/* Brand & Classification */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        <Link to="/dashboard" style={{ display: "flex", alignItems: "center", gap: "12px", textDecoration: "none" }}>
          <div style={{
            background: "linear-gradient(135deg, #0284c7 0%, #2563eb 100%)",
            color: "white",
            fontWeight: 800,
            fontSize: "13px",
            letterSpacing: "0.05em",
            padding: "5px 9px",
            borderRadius: "6px",
            boxShadow: "0 0 12px rgba(14, 165, 233, 0.4)"
          }}>
            SIH26117
          </div>
          <div>
            <div style={{ color: "#f8fafc", fontWeight: 700, fontSize: "14px", letterSpacing: "-0.01em" }}>
              SOVEREIGN INDUSTRIAL WORKBENCH
            </div>
            <div style={{ color: "#64748b", fontSize: "10px", fontWeight: 600, letterSpacing: "0.08em" }}>
              AIR-GAPPED AGENTIC KNOWLEDGE WORKER
            </div>
          </div>
        </Link>

        <span className="badge badge-sovereign" style={{ marginLeft: "8px" }}>
          🔒 RESTRICTED // ON-PREMISE AIR-GAP
        </span>
      </div>

      {/* Model Router Status & Engine Mode Toggle */}
      <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
        <div style={{
          background: "rgba(15, 23, 42, 0.8)",
          border: "1px solid #1e293b",
          borderRadius: "8px",
          padding: "5px 12px",
          fontSize: "11px",
          color: "#94a3b8",
          display: "flex",
          alignItems: "center",
          gap: "8px"
        }}>
          <span style={{ color: "#38bdf8", fontWeight: 600 }}>ROUTER:</span>
          <span>Auto (DeepSeek-R1 / Qwen-2.5 / Llava)</span>
        </div>

        {/* Backend / Simulator Mode Indicator & Toggle */}
        <button
          onClick={handleToggleMode}
          title="Click to toggle between Live API and Sovereign Simulator Mode"
          style={{
            background: isSimulator ? "rgba(245, 158, 11, 0.1)" : "rgba(16, 185, 129, 0.1)",
            border: `1px solid ${isSimulator ? "rgba(245, 158, 11, 0.4)" : "rgba(16, 185, 129, 0.4)"}`,
            color: isSimulator ? "#fbbf24" : "#34d399",
            borderRadius: "8px",
            padding: "5px 12px",
            fontSize: "11px",
            fontWeight: 600,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "6px"
          }}
        >
          <span style={{
            width: "7px",
            height: "7px",
            borderRadius: "50%",
            background: isSimulator ? "#fbbf24" : "#10b981",
            display: "inline-block"
          }} />
          {backendStatus} (Toggle)
        </button>

        {/* Lead Auditor Avatar & Sign Out */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginLeft: "10px" }}>
          <div style={{ textAlign: "right" }}>
            <div style={{ color: "#f1f5f9", fontSize: "12px", fontWeight: 600 }}>Nithin (Team Lead)</div>
            <div style={{ color: "#64748b", fontSize: "10px" }}>Lead Industrial Auditor</div>
          </div>
          <button
            onClick={handleSignOut}
            className="btn btn-secondary btn-sm"
            style={{ fontSize: "11px", padding: "4px 9px" }}
          >
            Exit
          </button>
        </div>
      </div>
    </header>
  );
}
