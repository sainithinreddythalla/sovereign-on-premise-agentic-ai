# SIH26117 — Sovereign On-Premise Agentic AI Workbench

## 1. PROJECT OVERVIEW

### Problem Statement

Industrial organizations such as refineries, PSUs, government organizations, and defence-linked manufacturing units handle highly confidential information.

Examples include:

- Engineering drawings
- P&IDs
- Inspection reports
- Maintenance documents
- Internal standards and manuals
- Scanned documents
- Handwritten notes
- Equipment photographs
- Financial information
- Internal source code
- Vendor information
- Project information
- Internal correspondence

Cloud-based AI assistants may not be suitable for such information because organizations require strong control over confidential data and AI processing.

The project aims to provide useful AI capabilities while keeping sensitive information within the organization's controlled environment.

---

## 2. PROJECT GOAL

Build a sovereign, self-hosted AI workbench for confidential industrial knowledge work.

The system should allow an organization to:

- Upload confidential documents.
- Understand text, scanned documents, tables, images, and engineering drawings.
- Search internal organizational knowledge using RAG.
- Select appropriate open-weight AI models for different tasks.
- Plan and execute multi-step tasks using an AI agent.
- Use controlled tools such as document readers and calculation tools.
- Ground important answers in source evidence.
- Verify important results.
- Generate useful work products such as reports, spreadsheets, and presentations.
- Operate without requiring external public AI APIs for the core confidential workflow.

The platform must be more than a generic chatbot.

---

## 3. CORE PRODUCT CONCEPT

The product is a:

**Sovereign Industrial AI Workbench**

The system should behave more like a secure AI worker for industrial knowledge tasks than a simple conversational assistant.

Core transformation:

```text
Confidential Data
        ↓
Understand
        ↓
Plan
        ↓
Retrieve
        ↓
Select Model
        ↓
Execute
        ↓
Verify
        ↓
Generate Deliverable
4. CORE PRINCIPLES
4.1 Sovereign
Sensitive information should remain inside the organization's controlled environment.
4.2 Multi-Model
The system should support multiple open-weight models instead of being permanently tied to one model.
4.3 Multimodal
The system should process:
Text
PDFs
Scanned documents
Images
Tables
Engineering drawings
Handwritten content where supported
4.4 Agentic
The AI should plan and execute multi-step tasks instead of only generating one-shot responses.
4.5 Verifiable
Important findings should be supported by:
Evidence
Source references
Verification information
Uncertainty indicators
4.6 Productive
The system should produce actual work products rather than only chat responses.
5. WHAT THE SYSTEM MUST NOT BE
The project must NOT be positioned as:
A generic chatbot
A simple ChatGPT clone
A simple Chat with PDF application
A basic RAG chatbot
A basic private LLM interface
A simple model selector
These may exist as components, but they are not the primary innovation.
6. MAIN DIFFERENTIATION
The project should differentiate itself through the combination of:
Confidential industrial workflows
Intelligent model routing
Multimodal industrial document understanding
Agentic task planning
Controlled tool execution
Internal knowledge grounding
Evidence-based reasoning
Result verification
Actual deliverable generation
Sovereign/self-hosted deployment
The system should demonstrate an end-to-end industrial task rather than only individual AI features.
7. PRIMARY DEMONSTRATION WORKFLOW
Confidential Industrial Engineering/Safety Audit
Example Inputs
P&ID / engineering drawing
Internal safety standard
Inspection report
Equipment photograph
Example User Request
"Audit this system against the applicable internal safety requirements, identify potential deviations with evidence, and prepare an approval/audit report."
Expected Workflow
User uploads documents
        ↓
Validate and store files
        ↓
Process documents
        ↓
Extract text, tables and images
        ↓
Index information
        ↓
Understand task
        ↓
Create task plan
        ↓
Retrieve relevant internal standards
        ↓
Select appropriate AI model
        ↓
Analyze documents/images
        ↓
Use controlled tools where required
        ↓
Generate potential findings
        ↓
Check findings against evidence
        ↓
Verify important results
        ↓
Attach evidence and sources
        ↓
Generate professional report
        ↓
User views/downloads report
Expected Output
Executive summary
Findings
Severity/status where applicable
Evidence
Source document
Page number where available
Recommendations
Verification status
Uncertainty/human-review indicators
Generated report
The system must not claim that an AI-generated result is an authoritative industrial fact without appropriate verification and human review.
8. HIGH-LEVEL ARCHITECTURE
USER
  |
  v
FRONTEND
React Web Application
  |
  | REST API
  v
BACKEND
FastAPI
  |
  +----------------+----------------+
  |                |                |
  v                v                v
AI / MODEL       RAG /            AGENT /
ROUTER           MULTIMODAL       WORKFLOW
  |                |                |
  +----------------+----------------+
                   |
                   v
            CONTROLLED TOOLS
       Files / Search / Calculation
                   |
                   v
             VERIFICATION
                   |
                   v
        DELIVERABLE GENERATION
                   |
          +--------+--------+
          |        |        |
         DOCX     XLSX     PPTX
         9. MODULE OWNERSHIP
Although the project is currently being developed by a solo developer, the architecture should remain modular as if multiple developers could work on it.
Module 1 — AI / LLM + Model Router
Responsibilities:
Open-weight model integration
Model abstraction
Model registry
Model routing
Text generation
Reasoning model integration
Vision-language model integration
Model health/status information
Prompt templates
AI service interface
The rest of the application must not depend directly on a specific model.
Models should be replaceable without major changes to frontend, backend, RAG or agent logic.
Module 2 — RAG + Multimodal Intelligence
Responsibilities:
PDF ingestion
Document parsing
OCR
Image extraction
Table extraction where practical
Text chunking
Embeddings
Vector search
Retrieval
Source/page tracking
Scanned document processing
Multimodal document processing
Every retrieved result should retain source information whenever available.
Module 3 — Agent + Industrial Workflow
Responsibilities:
Task understanding
Task planning
Multi-step execution
Tool calling
RAG coordination
AI model coordination
Industrial audit workflow
Finding generation
Verification orchestration
Report-generation workflow
The agent should use controlled tools rather than arbitrary unrestricted system access.
Module 4 — Backend / API
Responsibilities:
FastAPI application
REST APIs
Request validation
Authentication
Authorization
Database interaction
Document metadata
Task management
Service orchestration
Report management
API error handling
The backend acts as the primary integration layer.
Module 5 — Frontend / UI
Responsibilities:
React web application
Login/authentication UI
Dashboard
Document upload
Document library
Task creation
AI workspace
Processing status
Agent progress
Findings display
Evidence/source display
Verification display
Report download
Error states
The frontend communicates with the backend through defined APIs.
The frontend must not directly depend on AI/RAG internal implementations.
Module 6 — Testing + Integration
Responsibilities:
Unit testing
API testing
Integration testing
End-to-end testing
Test documents
Test scenarios
Regression testing
Module compatibility
Bug tracking
Performance checks
Final demo validation
Testing should happen continuously during development.
10. DEVELOPMENT AND INTEGRATION PRINCIPLE
The system must be modular.
Shared interfaces must be defined before implementation.
Internal implementation may change freely within a module, but shared contracts should remain stable.
Primary communication path:
Frontend
   ↓
Backend API
   ↓
Agent
   ↓
AI / RAG / Tools
The frontend must never depend directly on internal AI/RAG/Agent code.
11. API CONTRACTS
These are initial shared contracts.
Changes to shared contracts should be documented before implementation.
11.1 Upload Document
POST /api/documents/uploadPOST /api/documents/upload
Request:
multipart/form-data
file
Response:
{
  "document_id": "doc_001",
  "filename": "Safety_Manual.pdf",
  "status": "processing"
}
11.2 Get Document Status
GET /api/documents/{document_id}
Response:
{
  "document_id": "doc_001",
  "filename": "Safety_Manual.pdf",
  "status": "completed"
}
Possible statuses:
uploaded
processing
completed
failed
11.3 Create Task
POST /api/tasks
Request:
{
  "message": "Audit this equipment against the safety standard.",
  "document_ids": [
    "doc_001",
    "doc_002"
  ]
}
Response:
{
  "task_id": "task_001",
  "status": "queued"
}
11.4 Get Task Status
GET /api/tasks/{task_id}
Response:
{
  "task_id": "task_001",
  "status": "completed",
  "answer": "Three potential deviations were identified.",
  "verification_status": "verified_with_evidence",
  "evidence_coverage": 0.92,
  "requires_human_review": true,
  "sources": [
    {
      "document_id": "doc_001",
      "filename": "Safety_Manual.pdf",
      "page": 17,
      "reference": "Relevant safety requirement..."
    }
  ],
  "findings": [],
  "report_id": "report_001"
}
Possible task statuses:
queued
planning
retrieving
analyzing
verifying
generating
completed
failed
11.5 RAG Search
POST /api/rag/search
Request:
{
  "query": "Applicable safety requirements",
  "document_ids": [
    "doc_001"
  ],
  "top_k": 5
}
Response:
{
  "results": [
    {
      "document_id": "doc_001",
      "filename": "Safety_Manual.pdf",
      "page": 17,
      "text": "Relevant document content...",
      "score": 0.91
    }
  ]
}
11.6 AI Generation
POST /api/ai/generate
Request:
{
  "task_type": "reasoning",
  "prompt": "Analyze the retrieved evidence.",
  "context": []
}
Response:
{
  "model": "selected-model",
  "answer": "...",
  "verification_status": "requires_review"
}
The model router internally selects the appropriate available model.
11.7 Generate Report
POST /api/reports/generate
Request:
{
  "task_id": "task_001",
  "format": "docx"
}
Response:
{
  "report_id": "report_001",
  "status": "generated",
  "filename": "industrial_audit_report.docx"
}
Supported formats may expand later.
12. DATA STORAGE
The system requires three main storage categories.
12.1 Application Metadata
A relational database should store:
Users
Documents
Tasks
Task status
Findings
Reports
Model metadata
Audit information
12.2 Document Storage
Uploaded files and generated deliverables must be stored separately from application metadata.
Safety_Manual.pdf
       ↓
Controlled File Storage
       ↓
document_id = doc_001
The database stores metadata associated with the document.
12.3 Vector Storage
Document
   ↓
Parser
   ↓
Text/Image Extraction
   ↓
Chunking
   ↓
Embeddings
   ↓
Vector Database
13. RAG FLOW
User Question
      ↓
Query Processing
      ↓
Embedding
      ↓
Vector Search
      ↓
Relevant Chunks
      ↓
Evidence Context
      ↓
LLM
      ↓
Grounded Answer
Retrieved information should preserve:
Document ID
Filename
Page number where available
Extracted text
Relevance score
14. AGENT FLOW
User Task
    ↓
Task Understanding
    ↓
Task Planning
    ↓
Select Required Actions
    |
    +--> RAG Search
    |
    +--> Vision Analysis
    |
    +--> Document Reading
    |
    +--> Calculation Tool
    |
    +--> AI Model
    |
    +--> Report Generation
    |
    ↓
Verification
    ↓
Final Findings
    ↓
Deliverable
The agent must not have unrestricted access to the operating system.
All tools must have controlled permissions.
15. VERIFICATION LAYER
The system should attempt to verify important outputs before presenting them as final findings.
Verification can include:
Checking whether claims have supporting sources
Comparing findings against retrieved requirements
Re-running calculations
Checking calculation consistency
Detecting unsupported claims
Checking missing evidence
Reporting uncertainty
Checking whether source evidence actually supports the finding
The system must not present an uncertain AI-generated claim as a confirmed industrial fact.
Where verification cannot be completed, the result should clearly indicate:
Requires human review
or
Verification incomplete
16. EVIDENCE AND GROUNDING
Important findings should provide evidence.
Example:
Finding:
Potential safety requirement mismatch

Source:
Safety_Manual.pdf

Page:
17

Requirement Evidence:
Relevant requirement text

Observed Evidence:
P&ID.pdf

Page:
4

Status:
Requires review
Evidence should be traceable back to uploaded documents wherever technically possible.
17. DELIVERABLE GENERATION
The system should generate actual work products.
Potential outputs:
DOCX reports
XLSX calculations
PPTX presentations
Structured summaries
Analysis results
Code files where applicable
The primary demonstration should prioritize a professional industrial audit/approval report.
18. SECURITY AND CONFIDENTIALITY
The core workflow must be designed for confidential information.
Principles:
Confidential documents remain inside the controlled deployment environment.
Public AI APIs must not be required for the core confidential workflow.
Open-weight models should be capable of local/self-hosted execution.
Access control should be implemented.
Sensitive information should not be unnecessarily exposed in logs.
File access should be controlled.
Tool execution should be sandboxed.
Generated files should have controlled access.
Important actions should be auditable.
Security features should be implemented progressively based on prototype requirements.
The prototype must not falsely claim to provide complete enterprise-grade security unless those controls have actually been implemented and tested.
19. TECHNOLOGY SELECTION PRINCIPLE
Technology choices must satisfy:
Local/self-hosted operation
Suitable licensing
Multimodal capability
Ease of development
Reliability
Hardware feasibility
Modular integration
Ability to replace components
No module should become permanently dependent on a technology unless the dependency is explicitly approved.
The exact technology stack should be finalized before major implementation.
20. DEVELOPMENT ENVIRONMENT
Initial development environment:
Local Windows development machine
AWS or another cloud platform is NOT a core development dependency.
The architecture should remain deployment-friendly so that private/cloud deployment can be added later without redesigning the core application.
Because development hardware may not have a dedicated AI GPU, the model layer must remain replaceable.
Development should not depend on running a large language model directly on the developer's laptop.
21. SUGGESTED REPOSITORY STRUCTURE
sih26117-sovereign-industrial-ai/
│
├── frontend/
├── backend/
├── ai/
├── rag/
├── agent/
├── integration-tests/
├── docs/
├── data/
│
├── PROJECT_SPEC.md
├── README.md
└── docker-compose.yml
The exact structure may be adjusted after technology selection.
22. GIT WORKFLOW
The main branch must remain stable.
Suggested branches:
main
feature/ai
feature/rag
feature/agent
feature/backend
feature/frontend
feature/integration
Rules:
Do not directly commit experimental work to main.
Work primarily within assigned modules.
Commit frequently with meaningful messages.
Test before creating a pull request.
Review changes before merging.
Do not overwrite another developer's work.
Resolve architectural conflicts before implementation.
Keep commits focused.
For solo development, these rules may be simplified, but main should still represent the stable version.
23. CHANGE MANAGEMENT
Ideas and improvements are encouraged.
Shared architecture changes should follow:
Idea
  ↓
Discuss
  ↓
Check impact
  ↓
Approve / Reject
  ↓
Update PROJECT_SPEC.md
  ↓
Implement
Changes that can normally be made independently:
Internal functions
UI styling
Component organization
Internal implementation details
Refactoring within a module
Changes requiring architectural consideration:
API request/response formats
Database schema
Shared data models
Model interfaces
Agent-tool interfaces
Authentication architecture
Repository structure
Core workflow
24. AI CODING TOOL RULE
AI coding assistants may be used for development.
Before making changes, the AI coding assistant should be instructed:
Read PROJECT_SPEC.md completely before making changes. Follow the defined architecture and API contracts. Work only on the requested feature or module. Do not unnecessarily modify unrelated modules. Do not change shared interfaces without approval. Do not invent major architecture changes without discussing them first. Test the changes before finishing.
AI-generated code must be reviewed and tested.
The AI coding assistant must not be allowed to blindly rewrite the entire project.
25. TESTING STRATEGY
Testing should happen continuously.
Level 1 — Unit Testing
Test individual:
Functions
Services
Components
Parsers
Retrieval logic
Model interfaces
Level 2 — API Testing
Test:
Request validation
Response contracts
Error handling
Upload APIs
Task APIs
RAG APIs
Report APIs
Level 3 — Module Integration
Test:
Backend ↔ AI
Backend ↔ RAG
Backend ↔ Agent
Agent ↔ Tools
Agent ↔ Verification
Level 4 — End-to-End
Test:
Upload
  ↓
Process
  ↓
RAG
  ↓
Create Task
  ↓
Plan
  ↓
Retrieve
  ↓
Analyze
  ↓
Verify
  ↓
Generate Report
  ↓
Download
Level 5 — Demo Validation
Run the exact final demonstration multiple times using a fixed test dataset.
26. PRIMARY SUCCESS CRITERIA
The prototype should successfully demonstrate:
Required
Confidential document upload
Document processing
RAG retrieval
Source references
AI reasoning
Agentic task execution
Multimodal processing where applicable
Model selection/routing
Verification
Final report generation
Strongly Desired
Interactive task progress
Multiple model support
Evidence/uncertainty indicators
Audit trail
Industrial-focused UI
Multiple deliverable formats
Local deployment using containers
27. SCOPE CONTROL
The project should prioritize a strong end-to-end workflow over a large number of disconnected features.
First make this pipeline work:
Upload Document
      ↓
Process
      ↓
RAG
      ↓
AI
      ↓
Agent
      ↓
Verification
      ↓
Report
Only after this pipeline works should additional features be added.
Avoid spending excessive time on:
Complex enterprise authentication
Advanced cloud deployment
Excessive UI animations
Large numbers of AI models
Features unrelated to the primary industrial workflow
28. FUTURE EXTENSIONS
Possible future features include:
Private cloud deployment
Air-gapped deployment
Advanced RBAC
Enterprise SSO
More industrial workflows
Advanced model routing
Model performance benchmarking
Human approval workflows
Advanced audit logs
Additional document formats
Additional multimodal models
Enterprise deployment management
These are not required for the initial prototype unless time permits.
29. DEFINITION OF DONE
A feature/module is considered complete only when:
Core functionality works.
It follows the agreed architecture.
It follows API/interface contracts.
Basic tests exist.
It does not break other modules.
Documentation is provided where necessary.
It can be integrated with the rest of the system.
The complete project is ready for demonstration only when the primary end-to-end workflow works reliably.
30. FINAL PRODUCT VISION
The final product should demonstrate:
"A sovereign industrial AI worker that can securely understand confidential multimodal information, plan and execute industrial knowledge tasks using appropriate local AI models and controlled tools, verify important results with evidence, and produce useful professional deliverables within the organization's controlled environment."
The product should be presented as:
Industrial AI Workbench
and not merely as a chatbot.
DEVELOPMENT PRIORITY
The project should be built in the following order:
PHASE 1
Project Foundation
        ↓
PHASE 2
FastAPI Backend
        ↓
PHASE 3
Document Upload & Storage
        ↓
PHASE 4
Document Processing
        ↓
PHASE 5
RAG
        ↓
PHASE 6
AI / Model Abstraction
        ↓
PHASE 7
Agent
        ↓
PHASE 8
Verification
        ↓
PHASE 9
Report Generation
        ↓
PHASE 10
React Frontend
        ↓
PHASE 11
End-to-End Integration
        ↓
PHASE 12
Testing & Demo
MOST IMPORTANT RULE
Do not build disconnected features.
Always prioritize the working end-to-end pipeline:
CONFIDENTIAL DOCUMENT
        ↓
UNDERSTAND
        ↓
RETRIEVE EVIDENCE
        ↓
PLAN
        ↓
SELECT MODEL
        ↓
ANALYZE
        ↓
VERIFY
        ↓
GENERATE INDUSTRIAL DELIVERABLE
