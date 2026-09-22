/**
 * SIH26117 — Sovereign Industrial AI Workbench
 * Primary Industrial Audit Dataset: Unit-4 Hydrocracker Safety & Compliance Audit
 */

export const INITIAL_DOCUMENTS = [
  {
    document_id: "doc_001",
    filename: "Refinery_Safety_Standard_STD-804.pdf",
    category: "Internal Standard",
    filesize: "1.8 MB",
    pages: 48,
    status: "completed",
    upload_date: "2026-09-06 09:15",
    chunks_indexed: 112,
    security_tag: "CONFIDENTIAL // REFINERY OPERATIONS",
    summary: "Internal standards for pressure vessels, relief valve intervals, minimum shell thickness calculations, and flare bypass interlocks."
  },
  {
    document_id: "doc_002",
    filename: "Hydrocracker_Unit4_PID_DWG-401.pdf",
    category: "P&ID / Engineering Drawing",
    filesize: "4.2 MB",
    pages: 12,
    status: "completed",
    upload_date: "2026-09-06 09:22",
    chunks_indexed: 38,
    security_tag: "RESTRICTED // ENGINEERING BLUEPRINT",
    summary: "Process & Instrumentation Diagram for Unit-4 Hydrocracker Reactor Loop, including V-401 Feed Drum, PSV-401, and flare header bypass line 04-P-201."
  },
  {
    document_id: "doc_003",
    filename: "Pressure_Vessel_V401_Inspection_Report.pdf",
    category: "NDT Inspection Log",
    filesize: "2.1 MB",
    pages: 24,
    status: "completed",
    upload_date: "2026-09-06 09:30",
    chunks_indexed: 64,
    security_tag: "CONFIDENTIAL // NDT QA LOG",
    summary: "Latest non-destructive ultrasonic thickness testing (UTM), corrosion rate analysis, and relief valve maintenance log for Vessel V-401."
  },
  {
    document_id: "doc_004",
    filename: "Equipment_Photo_PSV401_Corrosion.svg",
    category: "Visual Inspection / Photo",
    filesize: "840 KB",
    pages: 1,
    status: "completed",
    upload_date: "2026-09-06 09:35",
    chunks_indexed: 6,
    security_tag: "CONFIDENTIAL // FIELD OBSERVATION",
    summary: "High-resolution optical inspection photograph of relief valve PSV-401 inlet flange showing atmospheric galvanic corrosion and illegible recalibration tag."
  }
];

export const AUDIT_PRESETS = [
  {
    id: "preset_hydrocracker_audit",
    name: "Primary Demo: Unit-4 Hydrocracker Safety Audit",
    prompt: "Audit this system against the applicable internal safety requirements, identify potential deviations with evidence, and prepare an approval/audit report.",
    document_ids: ["doc_001", "doc_002", "doc_003", "doc_004"],
    preferred_model: "Auto (Intelligent Sovereign Router)"
  },
  {
    id: "preset_psv_compliance",
    name: "Relief Device & PSV Recertification Check",
    prompt: "Examine all relief devices and overpressure safety equipment against mandatory service intervals and calibration logs.",
    document_ids: ["doc_001", "doc_003", "doc_004"],
    preferred_model: "DeepSeek-R1 (Local Reasoning)"
  },
  {
    id: "preset_corrosion_life",
    name: "Corrosion Allowance & Vessel Remaining Life Assessment",
    prompt: "Analyze ultrasonic wall thickness data, compute corrosion rates per ASME Section VIII, and flag containment hazards.",
    document_ids: ["doc_001", "doc_003"],
    preferred_model: "Qwen-2.5-Coder (Engineering Math)"
  }
];

export const MOCK_FINDINGS = [
  {
    finding_id: "FND-001",
    title: "Pressure Vessel V-401 Shell Wall Thickness Degradation Below Code Minimum",
    severity: "critical",
    category: "Mechanical Integrity & Containment",
    status: "Requires Immediate Remediation",
    requirement_source: {
      document_id: "doc_001",
      filename: "Refinery_Safety_Standard_STD-804.pdf",
      page: 17,
      section: "§5.1 Minimum Shell Thickness & Design Margins"
    },
    requirement_text: "Minimum allowable shell thickness for high-pressure reactor feed drum V-401 operating at 2.4 MPa design pressure shall be 12.50 mm (inclusive of 3.0 mm minimum corrosion allowance under sour service guidelines).",
    observed_source: {
      document_id: "doc_003",
      filename: "Pressure_Vessel_V401_Inspection_Report.pdf",
      page: 4,
      section: "§3.2 Ultrasonic Thickness Measurement (UTM) Summary"
    },
    observed_text: "Ultrasonic thickness measurement at C-ring sector reveals nominal shell wall thickness has diminished to 11.20 mm due to localized sour H2S gas thinning. Current thickness is 1.30 mm below the mandatory code threshold (10.4% deficiency).",
    verification_status: "verified_with_evidence",
    verification_notes: "ASME Section VIII Div 1 calculation verified by engineering tool: t_min = (P*R)/(S*E - 0.6*P) + CA = 12.50 mm. Calculated safety margin is compromised (0.896 vs 1.000 minimum).",
    requires_human_review: false,
    recommendation: "Immediately de-rate unit operating pressure to 1.95 MPa maximum. Issue immediate work order for automated phased array ultrasonic re-inspection and schedule weld overlay repair within 7 business days."
  },
  {
    finding_id: "FND-002",
    title: "Overdue Safety Relief Valve (PSV-401) Recalibration Interval",
    severity: "high",
    category: "Overpressure Protection",
    status: "Overdue Compliance Flag",
    requirement_source: {
      document_id: "doc_001",
      filename: "Refinery_Safety_Standard_STD-804.pdf",
      page: 9,
      section: "§4.2 Pressure Safety Valve Bench-Testing & Certification"
    },
    requirement_text: "All pressure safety valves (PSVs) installed on sour hydrocarbon service circuits shall be removed, bench-tested, recertified, and recalibrated at intervals not exceeding 12 months.",
    observed_source: {
      document_id: "doc_003",
      filename: "Pressure_Vessel_V401_Inspection_Report.pdf",
      page: 8,
      section: "§6.1 Relief Device Audit Log & Stamped Records"
    },
    observed_text: "PSV-401 physical tag inspection indicates last bench calibration date stamped 2024-11-12. Elapsed operating duration is currently 22 months without required re-certification or valve overhaul.",
    verification_status: "verified_with_evidence",
    verification_notes: "Elapsed service window verified: 668 days (> 365 days statutory refinery limit). Corroborated by optical flange photograph in doc_004 showing degraded lead seal.",
    requires_human_review: false,
    recommendation: "Issue emergency maintenance permit for online spare valve swap-out within 48 hours. Off-line pop-test the decommissioned valve to record set-pressure deviation."
  },
  {
    finding_id: "FND-003",
    title: "Emergency Depressuring Bypass Valve Indicated in Unauthorized Normal Open State",
    severity: "medium",
    category: "Process Safety & Containment",
    status: "Administrative & Field Discrepancy",
    requirement_source: {
      document_id: "doc_001",
      filename: "Refinery_Safety_Standard_STD-804.pdf",
      page: 22,
      section: "§6.3 Flare Header Bypass Isolation & Car-Seal Protocols"
    },
    requirement_text: "Emergency depressuring line manual bypass valves (HV-401B series) must remain chained and locked in the CLOSED position (Car-Seal Closed) during normal operating cycles.",
    observed_source: {
      document_id: "doc_002",
      filename: "Hydrocracker_Unit4_PID_DWG-401.pdf",
      page: 1,
      section: "Sheet 4, Coordinate C-2"
    },
    observed_text: "Line 04-P-201-CS shows bypass valve HV-401B tagged as 'Normally Open (NO)' without corresponding Management of Change (MOC) override annotation in drawing revision block.",
    verification_status: "requires_human_review",
    verification_notes: "Drawing notation indicates 'NO'. Discrepancy may represent an unapproved drawing update or active field violation. Requires physical field confirmation prior to sign-off.",
    requires_human_review: true,
    recommendation: "Field operations supervisor must perform an immediate physical lock-out/tag-out audit at Valve HV-401B manifold and cross-reference MOC Register #2026-MOC-089."
  }
];

export const MOCK_TASK_EXECUTION = {
  task_id: "task_hc_demo_001",
  status: "completed",
  answer: "Audit completed successfully across 4 confidential documents. Three potential deviations were identified: 1 Critical wall thickness deficit, 1 High overdue relief device calibration, and 1 Medium drawing bypass configuration discrepancy requiring human physical sign-off.",
  verification_status: "verified_with_evidence",
  evidence_coverage: 0.94,
  requires_human_review: true,
  sources: [
    {
      document_id: "doc_001",
      filename: "Refinery_Safety_Standard_STD-804.pdf",
      page: 17,
      reference: "§5.1 Minimum Shell Thickness — Requires 12.50 mm minimum for V-401 drum."
    },
    {
      document_id: "doc_001",
      filename: "Refinery_Safety_Standard_STD-804.pdf",
      page: 9,
      reference: "§4.2 Relief Valves — 12-month maximum interval for sour service PSVs."
    },
    {
      document_id: "doc_001",
      filename: "Refinery_Safety_Standard_STD-804.pdf",
      page: 22,
      reference: "§6.3 Flare Isolation — HV-401B bypass valve must remain Car-Seal Closed."
    },
    {
      document_id: "doc_003",
      filename: "Pressure_Vessel_V401_Inspection_Report.pdf",
      page: 4,
      reference: "§3.2 UTM Log — Actual measured wall thickness is 11.20 mm (1.30 mm deficit)."
    },
    {
      document_id: "doc_003",
      filename: "Pressure_Vessel_V401_Inspection_Report.pdf",
      page: 8,
      reference: "§6.1 Maintenance Log — PSV-401 last calibrated 2024-11-12 (22 months elapsed)."
    },
    {
      document_id: "doc_002",
      filename: "Hydrocracker_Unit4_PID_DWG-401.pdf",
      page: 1,
      reference: "Sheet 4, C-2 — Valve HV-401B annotated as 'Normally Open'."
    }
  ],
  findings: MOCK_FINDINGS,
  report_id: "report_hc_001",
  execution_steps: [
    {
      step: 1,
      phase: "queued",
      label: "Task Queued & Sovereign Check",
      timestamp: "10:00:01",
      status: "done",
      detail: "Audit request registered. Confidentiality scope confirmed: Air-gapped / Zero cloud exfiltration."
    },
    {
      step: 2,
      phase: "planning",
      label: "Task Understanding & Model Routing",
      timestamp: "10:00:03",
      status: "done",
      detail: "Agent formulated 4-stage audit plan. Routed reasoning to DeepSeek-R1 (local) and P&ID vision analysis to Qwen-VL (local)."
    },
    {
      step: 3,
      phase: "retrieving",
      label: "Grounded RAG Search",
      timestamp: "10:00:07",
      status: "done",
      detail: "Retrieved 8 confidential chunks across STD-804, DWG-401, and Inspection Log. Relevance score: 0.94."
    },
    {
      step: 4,
      phase: "analyzing",
      label: "Multimodal Analysis & Controlled Tools",
      timestamp: "10:00:12",
      status: "done",
      detail: "Invoked controlled engineering calculator tool for ASME wall thickness and optical tag parser for PSV inspection photo."
    },
    {
      step: 5,
      phase: "verifying",
      label: "Automated Evidence Verification",
      timestamp: "10:00:16",
      status: "done",
      detail: "Verified claims against source text. Wall thickness deficit confirmed by ASME formula. Bypass valve flagged for human review."
    },
    {
      step: 6,
      phase: "generating",
      label: "Deliverable Compilation",
      timestamp: "10:00:19",
      status: "done",
      detail: "Generated professional Industrial Audit Report (DOCX), Compliance Matrix (XLSX), and Executive Deck (PPTX)."
    },
    {
      step: 7,
      phase: "completed",
      label: "Audit Finalized & Signed-Off",
      timestamp: "10:00:21",
      status: "done",
      detail: "Ready for Lead Auditor download and operational review."
    }
  ]
};

export const INITIAL_DELIVERABLES = [
  {
    report_id: "report_hc_001",
    task_id: "task_hc_demo_001",
    filename: "Unit4_Hydrocracker_Safety_Audit_Report.docx",
    format: "docx",
    title: "Confidential Industrial Engineering & Safety Audit Report",
    unit: "Hydrocracker Complex // Unit-4",
    generated_at: "2026-09-06 10:00:21",
    filesize: "412 KB",
    evidence_coverage: "94%",
    verification_status: "Verified with Evidence",
    requires_human_review: true
  },
  {
    report_id: "report_hc_002",
    task_id: "task_hc_demo_001",
    filename: "Unit4_Audit_Deviations_Matrix.xlsx",
    format: "xlsx",
    title: "Mechanical Integrity & Non-Conformance Tracker",
    unit: "Hydrocracker Complex // Unit-4",
    generated_at: "2026-09-06 10:00:21",
    filesize: "158 KB",
    evidence_coverage: "94%",
    verification_status: "Verified with Evidence",
    requires_human_review: true
  },
  {
    report_id: "report_hc_003",
    task_id: "task_hc_demo_001",
    filename: "Unit4_Executive_Safety_Briefing.pptx",
    format: "pptx",
    title: "Executive Audit Summary Deck (Operations Committee)",
    unit: "Hydrocracker Complex // Unit-4",
    generated_at: "2026-09-06 10:00:21",
    filesize: "890 KB",
    evidence_coverage: "94%",
    verification_status: "Verified with Evidence",
    requires_human_review: true
  }
];
