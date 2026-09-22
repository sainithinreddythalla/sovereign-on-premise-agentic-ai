import React from "react";

export default function StatusBadge({ type, value, label }) {
  if (type === "severity") {
    const sev = (value || "").toLowerCase();
    if (sev === "critical") {
      return <span className="badge badge-critical">● CRITICAL NON-COMPLIANCE</span>;
    }
    if (sev === "high") {
      return <span className="badge badge-high">▲ HIGH PRIORITY</span>;
    }
    if (sev === "medium") {
      return <span className="badge badge-medium">■ MEDIUM DEVIATION</span>;
    }
    return <span className="badge" style={{ background: "rgba(148, 163, 184, 0.1)", color: "#cbd5e1" }}>◆ OBSERVATION</span>;
  }

  if (type === "verification") {
    const ver = (value || "").toLowerCase();
    if (ver === "verified_with_evidence") {
      return (
        <span className="badge badge-verified" title="Verified against source text and mathematical equations">
          ✓ VERIFIED WITH EVIDENCE
        </span>
      );
    }
    if (ver === "requires_human_review" || ver === "requires_review") {
      return (
        <span className="badge badge-review" title="Field physical check or engineer review required">
          ⚠ REQUIRES HUMAN REVIEW
        </span>
      );
    }
    return (
      <span className="badge badge-critical" title="Lacks adequate source evidence">
        ✕ UNVERIFIED CLAIM
      </span>
    );
  }

  return <span className="badge badge-sovereign">{label || value}</span>;
}
