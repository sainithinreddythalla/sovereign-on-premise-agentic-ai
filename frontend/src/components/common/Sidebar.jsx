import React from "react";
import { NavLink } from "react-router-dom";

export default function Sidebar() {
  const navItems = [
    {
      to: "/dashboard",
      label: "Dashboard",
      icon: "📊",
      desc: "System health & audit metrics"
    },
    {
      to: "/workspace",
      label: "Audit Workspace",
      icon: "⚡",
      desc: "Multi-model agentic worker"
    },
    {
      to: "/documents",
      label: "Confidential Hub",
      icon: "📁",
      desc: "P&IDs, standards & logs"
    },
    {
      to: "/deliverables",
      label: "Deliverables & Reports",
      icon: "📋",
      desc: "DOCX, XLSX & PPTX audit files"
    }
  ];

  return (
    <aside style={{
      width: "260px",
      background: "#0c121e",
      borderRight: "1px solid #1e293b",
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-between",
      padding: "20px 14px",
      minHeight: "calc(100vh - 64px)"
    }}>
      <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
        <div style={{
          fontSize: "10px",
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          color: "#475569",
          padding: "0 12px 8px 12px",
          fontWeight: 700
        }}>
          Industrial AI Modules
        </div>

        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            style={({ isActive }) => ({
              display: "flex",
              alignItems: "center",
              gap: "12px",
              padding: "10px 14px",
              borderRadius: "8px",
              textDecoration: "none",
              color: isActive ? "#ffffff" : "#94a3b8",
              background: isActive
                ? "linear-gradient(90deg, rgba(37, 99, 235, 0.25) 0%, rgba(37, 99, 235, 0.08) 100%)"
                : "transparent",
              border: isActive ? "1px solid rgba(59, 130, 246, 0.4)" : "1px solid transparent",
              transition: "all 0.15s ease-in-out"
            })}
          >
            <span style={{ fontSize: "16px" }}>{item.icon}</span>
            <div>
              <div style={{ fontSize: "13px", fontWeight: 600 }}>{item.label}</div>
              <div style={{ fontSize: "10px", color: "#64748b" }}>{item.desc}</div>
            </div>
          </NavLink>
        ))}
      </div>

      {/* Sovereign Assurance Badge Box */}
      <div style={{
        background: "rgba(15, 23, 42, 0.7)",
        border: "1px solid #1e293b",
        borderRadius: "10px",
        padding: "14px",
        fontSize: "11px"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#38bdf8", fontWeight: 700, marginBottom: "8px" }}>
          <span>🛡️</span> SOVEREIGN ASSURANCE
        </div>
        <div style={{ color: "#94a3b8", fontSize: "11px", display: "flex", flexDirection: "column", gap: "5px" }}>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span>Cloud Exfiltration:</span>
            <strong style={{ color: "#10b981" }}>0% (Zero)</strong>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span>Vector RAG:</span>
            <strong style={{ color: "#f8fafc" }}>Local Dense</strong>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span>Tool Permissions:</span>
            <strong style={{ color: "#f8fafc" }}>Sandboxed</strong>
          </div>
        </div>
        <div style={{
          marginTop: "10px",
          paddingTop: "8px",
          borderTop: "1px solid #1e293b",
          fontSize: "10px",
          color: "#64748b",
          textAlign: "center"
        }}>
          Air-Gapped Refinery Enclave
        </div>
      </div>
    </aside>
  );
}
