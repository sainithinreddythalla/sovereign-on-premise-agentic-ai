import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("lead.auditor@refinery.internal");
  const [password, setPassword] = useState("••••••••••••");

  const handleSubmit = (e) => {
    e.preventDefault();
    navigate("/dashboard");
  };

  const handleQuickDemo = () => {
    navigate("/dashboard");
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "radial-gradient(ellipse at top, #111e38 0%, #080c14 100%)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: "24px"
    }}>
      {/* Security Classification Banner */}
      <div style={{
        background: "rgba(239, 68, 68, 0.12)",
        border: "1px solid rgba(239, 68, 68, 0.35)",
        color: "#fca5a5",
        fontSize: "11px",
        fontWeight: 700,
        letterSpacing: "0.1em",
        padding: "6px 20px",
        borderRadius: "9999px",
        marginBottom: "28px",
        display: "flex",
        alignItems: "center",
        gap: "8px"
      }}>
        <span>⚠️</span> CONFIDENTIAL INDUSTRIAL WORKBENCH — RESTRICTED ACCESS ONLY
      </div>

      <div style={{
        background: "#0f172a",
        border: "1px solid #1e293b",
        borderRadius: "16px",
        width: "440px",
        maxWidth: "100%",
        padding: "40px",
        boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.7)",
        position: "relative"
      }}>
        {/* Top Sovereign Badge */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
          <div style={{
            background: "linear-gradient(135deg, #0284c7 0%, #2563eb 100%)",
            color: "white",
            fontWeight: 800,
            fontSize: "13px",
            padding: "4px 10px",
            borderRadius: "6px"
          }}>
            SIH26117
          </div>
          <span className="badge badge-sovereign" style={{ fontSize: "10px" }}>
            AIR-GAPPED SYSTEM
          </span>
        </div>

        <h1 style={{
          fontSize: "22px",
          fontWeight: 800,
          color: "#f8fafc",
          marginBottom: "6px",
          letterSpacing: "-0.02em"
        }}>
          Sovereign AI Workbench
        </h1>
        <p style={{
          fontSize: "13px",
          color: "#94a3b8",
          marginBottom: "28px",
          lineHeight: "1.4"
        }}>
          Confidential industrial knowledge work, multimodal document understanding, and engineering safety audits.
        </p>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "#cbd5e1", marginBottom: "6px" }}>
              Internal Organization Email
            </label>
            <input
              type="email"
              className="input-field"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="operator@refinery.gov.in"
              required
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "#cbd5e1", marginBottom: "6px" }}>
              Air-Gapped Access Key
            </label>
            <input
              type="password"
              className="input-field"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: "100%", marginTop: "8px", padding: "12px" }}
          >
            Authenticate Industrial Access
          </button>
        </form>

        <div style={{
          margin: "20px 0",
          display: "flex",
          alignItems: "center",
          gap: "12px",
          color: "#475569",
          fontSize: "11px"
        }}>
          <div style={{ flex: 1, height: "1px", background: "#1e293b" }} />
          <span>EVALUATION ACCESS</span>
          <div style={{ flex: 1, height: "1px", background: "#1e293b" }} />
        </div>

        {/* Instant Evaluation Demo Login */}
        <button
          type="button"
          onClick={handleQuickDemo}
          className="btn btn-secondary"
          style={{
            width: "100%",
            border: "1px dashed #38bdf8",
            background: "rgba(56, 189, 248, 0.06)",
            color: "#38bdf8"
          }}
        >
          ⚡ Quick Demo Login as Lead Auditor
        </button>

        {/* Sovereignty Guarantees */}
        <div style={{
          marginTop: "28px",
          paddingTop: "20px",
          borderTop: "1px solid #1e293b",
          fontSize: "11px",
          color: "#64748b",
          display: "flex",
          flexDirection: "column",
          gap: "6px"
        }}>
          <div>🔒 Zero data leaves your private enterprise perimeter.</div>
          <div>⚡ Powered by local open-weight models (DeepSeek, Qwen, Llava).</div>
        </div>
      </div>
    </div>
  );
}
