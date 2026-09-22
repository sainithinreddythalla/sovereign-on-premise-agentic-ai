/**
 * SIH26117 — Centralized API Client
 * Supports:
 *  - Live FastAPI Backend
 *  - Sovereign In-Browser Simulator
 *  - Genuine XLSX / PPTX downloads
 *  - Real/static backend-generated DOCX download
 */

import {
  INITIAL_DOCUMENTS,
  MOCK_TASK_EXECUTION,
  INITIAL_DELIVERABLES
} from "./mockData";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

/*
 * API_BASE_URL normally ends with /api.
 * Backend health endpoint is /health, not /api/health.
 */
const BACKEND_BASE_URL = API_BASE_URL.replace(/\/api\/?$/, "");

// ============================================================
// Local simulator state
// ============================================================

let localDocuments = [...INITIAL_DOCUMENTS];
let localDeliverables = [...INITIAL_DELIVERABLES];

let isSimulatorMode = true;

// ============================================================
// Helpers
// ============================================================

const saveBlob = (blob, filename) => {
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;

  document.body.appendChild(a);
  a.click();
  a.remove();

  setTimeout(() => {
    URL.revokeObjectURL(url);
  }, 1000);
};

// ============================================================
// Backend health
// ============================================================

export const checkBackendHealth = async () => {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/health`, {
      method: "GET"
    });

    if (!res.ok) {
      throw new Error(`Backend health HTTP ${res.status}`);
    }

    const data = await res.json();

    isSimulatorMode = false;

    console.log("SOVEREIGN BACKEND ONLINE:", data);

    return {
      online: true,
      mode: "Live Backend",
      data
    };
  } catch (err) {
    console.warn(
      "Backend unavailable. Using Sovereign Local Simulator:",
      err
    );

    isSimulatorMode = true;

    return {
      online: false,
      mode: "Sovereign Local Simulator"
    };
  }
};

export const getSimulatorMode = () => isSimulatorMode;

export const setSimulatorMode = (enabled) => {
  isSimulatorMode = enabled;
};

// ============================================================
// 11.1 Upload Document
// POST /api/documents/upload
// ============================================================

export const uploadDocument = async (file) => {
  if (!isSimulatorMode) {
    try {
      const formData = new FormData();

      formData.append("file", file);

      const res = await fetch(
        `${API_BASE_URL}/documents/upload`,
        {
          method: "POST",
          body: formData
        }
      );

      if (!res.ok) {
        throw new Error(`Upload failed: HTTP ${res.status}`);
      }

      return await res.json();
    } catch (err) {
      console.warn(
        "Live upload failed, falling back to simulator:",
        err
      );
    }
  }

  const newDoc = {
    document_id: `doc_${Date.now().toString().slice(-4)}`,

    filename: file.name,

    category:
      file.name.endsWith(".pdf")
        ? "Confidential PDF"
        : file.name.endsWith(".svg") ||
          file.name.endsWith(".png")
        ? "Optical Drawing / Photo"
        : "Confidential Document",

    filesize: `${(
      file.size /
      (1024 * 1024)
    ).toFixed(2)} MB`,

    pages: Math.floor(Math.random() * 20) + 1,

    status: "completed",

    upload_date: new Date()
      .toISOString()
      .replace("T", " ")
      .substring(0, 16),

    chunks_indexed:
      Math.floor(Math.random() * 40) + 8,

    security_tag:
      "RESTRICTED // LOCAL AIR-GAP",

    summary:
      `Ingested confidential document: ${file.name}. ` +
      "Processed with local parser and indexed into sovereign vector database."
  };

  localDocuments.unshift(newDoc);

  return {
    document_id: newDoc.document_id,
    filename: newDoc.filename,
    status: "processing"
  };
};

// ============================================================
// 11.2 Get Document Status
// GET /api/documents/{id}
// ============================================================

export const getDocumentStatus = async (documentId) => {
  if (!isSimulatorMode) {
    try {
      const res = await fetch(
        `${API_BASE_URL}/documents/${documentId}`
      );

      if (!res.ok) {
        throw new Error(
          `Document status HTTP ${res.status}`
        );
      }

      return await res.json();
    } catch (err) {
      console.warn(
        "Live document status failed, using simulator:",
        err
      );
    }
  }

  const doc = localDocuments.find(
    (d) => d.document_id === documentId
  );

  return (
    doc || {
      document_id: documentId,
      filename: "Unknown.pdf",
      status: "completed"
    }
  );
};

// ============================================================
// List Documents
// ============================================================

export const listDocuments = async () => {
  if (!isSimulatorMode) {
    try {
      const res = await fetch(
        `${API_BASE_URL}/documents`
      );

      if (!res.ok) {
        throw new Error(
          `Document list HTTP ${res.status}`
        );
      }

      return await res.json();
    } catch (err) {
      console.warn(
        "Live list documents failed, using simulator:",
        err
      );
    }
  }

  return localDocuments;
};

// ============================================================
// 11.3 Create Task
// POST /api/tasks
// ============================================================

export const createTask = async ({
  message,
  document_ids,
  preferred_model
}) => {
  if (!isSimulatorMode) {
    try {
      const res = await fetch(
        `${API_BASE_URL}/tasks`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            message,
            document_ids,
            preferred_model
          })
        }
      );

      if (!res.ok) {
        throw new Error(
          `Task creation HTTP ${res.status}`
        );
      }

      return await res.json();
    } catch (err) {
      console.warn(
        "Live createTask failed, using simulator:",
        err
      );
    }
  }

  return {
    task_id: `task_${Date.now().toString().slice(-4)}`,
    status: "queued"
  };
};

// ============================================================
// 11.4 Get Task Status
// GET /api/tasks/{task_id}
// ============================================================

export const getTaskStatus = async (taskId) => {
  if (!isSimulatorMode) {
    try {
      const res = await fetch(
        `${API_BASE_URL}/tasks/${taskId}`
      );

      if (!res.ok) {
        throw new Error(
          `Task status HTTP ${res.status}`
        );
      }

      return await res.json();
    } catch (err) {
      console.warn(
        "Live getTaskStatus failed, using simulator:",
        err
      );
    }
  }

  return {
    ...MOCK_TASK_EXECUTION,
    task_id: taskId
  };
};

// ============================================================
// 11.5 RAG Search
// POST /api/rag/search
// ============================================================

export const searchRAG = async ({
  query,
  document_ids = [],
  top_k = 5
}) => {
  if (!isSimulatorMode) {
    try {
      const res = await fetch(
        `${API_BASE_URL}/rag/search`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            query,
            document_ids,
            top_k
          })
        }
      );

      if (!res.ok) {
        throw new Error(
          `RAG search HTTP ${res.status}`
        );
      }

      return await res.json();
    } catch (err) {
      console.warn(
        "Live RAG search failed, using simulator:",
        err
      );
    }
  }

  return {
    results: [
      {
        document_id: "doc_001",

        filename:
          "Refinery_Safety_Standard_STD-804.pdf",

        page: 17,

        text:
          "Section 5.1: Minimum allowable shell thickness " +
          "for high-pressure reactor feed drum V-401 " +
          "operating at 2.4 MPa design pressure shall be " +
          "12.50 mm (inclusive of 3.0 mm corrosion allowance).",

        score: 0.96
      },

      {
        document_id: "doc_001",

        filename:
          "Refinery_Safety_Standard_STD-804.pdf",

        page: 9,

        text:
          "Section 4.2: Pressure safety valves (PSVs) " +
          "installed on sour hydrocarbon service circuits " +
          "shall be bench-tested and recertified at " +
          "intervals not exceeding 12 months.",

        score: 0.93
      },

      {
        document_id: "doc_003",

        filename:
          "Pressure_Vessel_V401_Inspection_Report.pdf",

        page: 4,

        text:
          "Section 3.2: Ultrasonic thickness measurement " +
          "indicates nominal shell thickness has diminished " +
          "to 11.20 mm due to localized sour gas thinning.",

        score: 0.91
      }
    ]
  };
};

// ============================================================
// 11.6 AI Generation
// POST /api/ai/generate
// ============================================================

export const generateAI = async ({
  task_type = "reasoning",
  prompt,
  context = []
}) => {
  if (!isSimulatorMode) {
    try {
      const res = await fetch(
        `${API_BASE_URL}/ai/generate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            task_type,
            prompt,
            context
          })
        }
      );

      if (!res.ok) {
        throw new Error(
          `AI generation HTTP ${res.status}`
        );
      }

      return await res.json();
    } catch (err) {
      console.warn(
        "Live AI generation failed, using simulator:",
        err
      );
    }
  }

  return {
    model:
      task_type === "vision"
        ? "qwen2-vl:7b-local"
        : "deepseek-r1:8b-local",

    answer:
      "Cross-referenced safety requirements against observations. " +
      "Identified 3 specific deviations with source citations.",

    verification_status:
      "verified_with_evidence"
  };
};

// ============================================================
// 11.7 Generate Report
// POST /api/reports/generate
// ============================================================

export const generateReport = async ({
  task_id,
  format = "docx"
}) => {
  if (!isSimulatorMode) {
    try {
      const res = await fetch(
        `${API_BASE_URL}/reports/generate`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            task_id,
            format
          })
        }
      );

      if (!res.ok) {
        throw new Error(
          `Report generation HTTP ${res.status}`
        );
      }

      const data = await res.json();

      return {
        ...data,
        task_id,
        format
      };
    } catch (err) {
      console.warn(
        "Live report generation failed, using simulator:",
        err
      );
    }
  }

  const newReport = {
    report_id:
      `report_${Date.now().toString().slice(-4)}`,

    task_id,

    filename:
      `Unit4_Industrial_Audit_Report_` +
      `${Date.now().toString().slice(-4)}.${format}`,

    format,

    title:
      `Industrial Safety & Engineering Audit Report ` +
      `(${format.toUpperCase()})`,

    unit:
      "Hydrocracker Complex // Unit-4",

    generated_at:
      new Date()
        .toISOString()
        .replace("T", " ")
        .substring(0, 19),

    filesize:
      format === "docx"
        ? "420 KB"
        : format === "xlsx"
        ? "165 KB"
        : "910 KB",

    evidence_coverage: "94%",

    verification_status:
      "Verified with Evidence",

    requires_human_review: true
  };

  localDeliverables.unshift(newReport);

  return {
    report_id: newReport.report_id,
    task_id,
    status: "generated",
    filename: newReport.filename,
    format
  };
};

// ============================================================
// List Generated Deliverables
// ============================================================

export const listDeliverables = async () => {
  return localDeliverables;
};

// ============================================================
// DOCX DOWNLOAD
// Uses valid static DOCX placed in frontend/public/reports
// ============================================================

const downloadDocx = async (report) => {
  const filename =
    report.filename ||
    "Unit4_Hydrocracker_Safety_Audit_Report.docx";

  const response = await fetch(
    "/reports/Unit4_Hydrocracker_Safety_Audit_Report.docx"
  );

  if (!response.ok) {
    throw new Error(
      `DOCX file unavailable: HTTP ${response.status}`
    );
  }

  const blob = await response.blob();

  saveBlob(blob, filename);
};

// ============================================================
// XLSX DOWNLOAD
// Genuine Excel workbook
// ============================================================

const downloadXlsx = async (report) => {
  const ExcelJS = await import("exceljs");

  const ExcelJSClass =
    ExcelJS.default || ExcelJS;

  const workbook =
    new ExcelJSClass.Workbook();

  workbook.creator = "SIH26117";

  workbook.company =
    "Sovereign Industrial AI Workbench";

  workbook.subject =
    "Industrial Safety Audit";

  workbook.title =
    "Unit-4 Hydrocracker Audit Findings";

  const worksheet =
    workbook.addWorksheet("Audit Findings");

  worksheet.columns = [
    {
      header: "Finding ID",
      key: "id",
      width: 14
    },
    {
      header: "Severity",
      key: "severity",
      width: 14
    },
    {
      header: "Category",
      key: "category",
      width: 28
    },
    {
      header: "Requirement",
      key: "requirement",
      width: 28
    },
    {
      header: "Req Page",
      key: "reqPage",
      width: 12
    },
    {
      header: "Observed Document",
      key: "document",
      width: 38
    },
    {
      header: "Obs Page",
      key: "obsPage",
      width: 12
    },
    {
      header: "Observed Measurement",
      key: "measurement",
      width: 38
    },
    {
      header: "Status",
      key: "status",
      width: 30
    },
    {
      header: "Verification",
      key: "verification",
      width: 30
    }
  ];

  worksheet.addRows([
    {
      id: "FND-001",
      severity: "CRITICAL",
      category: "Mechanical Integrity",
      requirement: "STD-804 §5.1",
      reqPage: 7,
      document:
        "Pressure Vessel V-401 Inspection Report",
      obsPage: 4,
      measurement:
        "11.20 mm; minimum required 12.50 mm",
      status:
        "Requires Immediate Remediation",
      verification:
        "Verified With Evidence"
    },

    {
      id: "FND-002",
      severity: "HIGH",
      category:
        "Overpressure Protection",
      requirement: "STD-804 §4.2",
      reqPage: 9,
      document:
        "Pressure Vessel V-401 Inspection Report",
      obsPage: 5,
      measurement:
        "Last calibration: 2024-11-12",
      status:
        "Overdue Recalibration",
      verification:
        "Verified With Evidence"
    },

    {
      id: "FND-003",
      severity: "MEDIUM",
      category:
        "Process Containment",
      requirement: "STD-804 §6.3",
      reqPage: 22,
      document:
        "Hydrocracker Unit-4 P&ID DWG-401",
      obsPage: 1,
      measurement:
        "HV-401B labeled Normally Open",
      status:
        "Review Required",
      verification:
        "Requires Human Review"
    }
  ]);

  worksheet.getRow(1).font = {
    bold: true
  };

  worksheet.freezePanes = {
    row: 1
  };

  worksheet.autoFilter = {
    from: "A1",
    to: "J4"
  };

  const buffer =
    await workbook.xlsx.writeBuffer();

  const blob = new Blob(
    [buffer],
    {
      type:
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }
  );

  saveBlob(
    blob,
    report.filename ||
      "Unit4_Hydrocracker_Audit_Findings.xlsx"
  );
};

// ============================================================
// PPTX DOWNLOAD
// Genuine PowerPoint presentation
// ============================================================

const downloadPptx = async (report) => {
  const PptxModule =
    await import("pptxgenjs");

  const PptxGenJS =
    PptxModule.default || PptxModule;

  const pptx =
    new PptxGenJS();

  pptx.author =
    "SIH26117";

  pptx.company =
    "Sovereign Industrial AI Workbench";

  pptx.subject =
    "Industrial Engineering and Safety Audit";

  pptx.title =
    "Unit-4 Hydrocracker Safety Audit";

  pptx.lang =
    "en-US";

  pptx.layout =
    "LAYOUT_WIDE";

  const addSlide = (
    title,
    body
  ) => {
    const slide =
      pptx.addSlide();

    slide.background = {
      color: "FFFFFF"
    };

    slide.addText(
      title,
      {
        x: 0.6,
        y: 0.45,
        w: 12.0,
        h: 0.7,
        fontSize: 25,
        bold: true,
        color: "1F2937",
        margin: 0
      }
    );

    slide.addText(
      body,
      {
        x: 0.8,
        y: 1.45,
        w: 11.4,
        h: 5.0,
        fontSize: 18,
        color: "374151",
        margin: 0.05,
        valign: "top",
        breakLine: false,
        fit: "shrink"
      }
    );

    return slide;
  };

  // Slide 1

  addSlide(
    "SIH26117 — Sovereign Industrial AI Audit",

    "Confidential Engineering & Safety Audit\n\n" +
    "Facility: Hydrocracker Complex — Unit-4\n" +
    "System: Reactor Feed Drum V-401 and PSV-401\n\n" +
    "Evidence-grounded local AI analysis"
  );

  // Slide 2

  addSlide(
    "FND-001 — Critical Finding",

    "Shell Wall Thickness Degradation\n\n" +
    "Observed thickness: 11.20 mm\n" +
    "Minimum requirement: 12.50 mm\n" +
    "Deficit: 1.30 mm\n\n" +
    "Verification: Verified With Evidence\n" +
    "Sources: STD-804 §5.1 and V-401 inspection report"
  );

  // Slide 3

  addSlide(
    "FND-002 — High Finding",

    "PSV-401 Recertification\n\n" +
    "Maximum test interval: 12 months\n" +
    "Last calibration: 2024-11-12\n\n" +
    "Status: Overdue Recalibration\n" +
    "Verification: Verified With Evidence"
  );

  // Slide 4

  addSlide(
    "FND-003 — Medium Finding",

    "HV-401B Normal State\n\n" +
    "P&ID indicates the valve as Normally Open.\n\n" +
    "Status: Potential Deviation\n" +
    "Verification: Requires Human Review\n\n" +
    "Physical field verification is required."
  );

  // Slide 5

  addSlide(
    "Evidence & Verification",

    "Evidence Coverage: 94%\n\n" +
    "Findings are linked to source documents " +
    "and page references.\n\n" +
    "Verified findings are evidence-supported.\n\n" +
    "Uncertain findings are explicitly marked " +
    "for human review."
  );

  await pptx.writeFile({
    fileName:
      report.filename ||
      "Unit4_Hydrocracker_Safety_Audit.pptx"
  });
};

// ============================================================
// Main Download Function
// ============================================================

export const downloadReportFile = async (
  report
) => {
  try {
    if (!report) {
      throw new Error(
        "No report information was provided."
      );
    }

    const filename =
      report.filename || "";

    const format =
      report.format ||
      (
        filename.endsWith(".docx")
          ? "docx"
          : filename.endsWith(".xlsx")
          ? "xlsx"
          : filename.endsWith(".pptx")
          ? "pptx"
          : ""
      );

    console.log(
      "Downloading report:",
      {
        report,
        format,
        API_BASE_URL,
        isSimulatorMode
      }
    );

    // --------------------------------------------------------
    // DOCX
    // --------------------------------------------------------

    if (
      format === "docx" ||
      filename.endsWith(".docx")
    ) {
      await downloadDocx(report);
      return;
    }

    // --------------------------------------------------------
    // XLSX
    // --------------------------------------------------------

    if (
      format === "xlsx" ||
      filename.endsWith(".xlsx")
    ) {
      await downloadXlsx(report);
      return;
    }

    // --------------------------------------------------------
    // PPTX
    // --------------------------------------------------------

    if (
      format === "pptx" ||
      filename.endsWith(".pptx")
    ) {
      await downloadPptx(report);
      return;
    }

    throw new Error(
      `Unsupported report format: ${format || "unknown"}`
    );

  } catch (error) {
    console.error(
      "Report download failed:",
      error
    );

    alert(
      `Unable to generate ${
        report?.format?.toUpperCase() || "report"
      }.\n\n${error.message}`
    );
  }
};