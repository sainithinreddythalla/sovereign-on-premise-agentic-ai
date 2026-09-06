SIH26117 — Sovereign On-Premise Agentic AI Workbench
1. Project Overview
Problem Statement
Industrial organizations such as refineries, PSUs, government organizations, and defence-linked manufacturing units handle highly confidential information.
Examples include:
Engineering drawings
P&IDs
Inspection reports
Maintenance documents
Internal standards and manuals
Scanned documents
Handwritten notes
Equipment photographs
Financial information
Internal source code
Vendor information
Project information
Internal correspondence
Cloud-based AI assistants may not be suitable for such information because organizations require strong control over confidential data and AI processing.
The project aims to provide useful AI capabilities while keeping sensitive information within the organization's controlled environment.
2. Project Goal
Build a sovereign, self-hosted AI workbench for confidential industrial knowledge work.
The system should allow an organization to:
Upload confidential documents.
Understand text, scanned documents, tables, images, and engineering drawings.
Search internal organizational knowledge using RAG.
Select appropriate open-weight AI models for different tasks.
Plan and execute multi-step tasks using an AI agent.
Use controlled tools such as document readers and calculation tools.
Ground important answers in source evidence.
Verify important results.
Generate useful work products such as reports, spreadsheets, and presentations.
Operate without requiring external public AI APIs for the core confidential workflow.
The platform must be more than a generic chatbot.
3. Core Product Concept
The product is a Sovereign Industrial AI Workbench.
The system should behave more like a secure AI worker for industrial knowledge tasks than a simple conversational assistant.
Core transformation:
Confidential Data → Understand → Plan → Retrieve → Select Model → Execute → Verify → Generate Deliverable
4. Core Principles
4.1 Sovereign
Sensitive information should remain inside the organization's controlled environment.
4.2 Multi-Model
The system should support multiple open-weight models instead of being permanently tied to one model.
4.3 Multimodal
The system should process text, PDFs, scanned documents, images, tables, engineering drawings, and handwritten content where supported.
4.4 Agentic
The AI should plan and execute multi-step tasks instead of only generating one-shot responses.
4.5 Verifiable
Important findings should be supported by evidence, source references, and verification information.
4.6 Productive
The system should produce actual work products rather than only chat responses.
5. What the System Must NOT Be
The project must NOT be positioned as:
A generic chatbot
A simple ChatGPT clone
A simple Chat with PDF application
A basic RAG chatbot
A basic private LLM interface
A simple model selector
These may exist as components, but they are not the primary innovation.
6. Main Differentiation
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
7. Primary Demonstration Workflow
Confidential Industrial Engineering/Safety Audit
Example inputs:
P&ID / engineering drawing
Internal safety standard
Inspection report
Equipment photograph
Example user request:
"Audit this system against the applicable internal safety requirements, identify deviations with evidence, and prepare an approval/audit report."
Expected workflow:
User uploads documents.
System validates and stores files.
Documents are processed.
Text, tables, and images are extracted.
Relevant information is indexed for retrieval.
Agent understands the task.
Agent creates a task plan.
RAG retrieves relevant internal standards.
Model Router selects appropriate AI models.
Multimodal models analyze drawings/images where required.
Agent performs required reasoning.
Controlled tools perform calculations or document operations where required.
Findings are generated.
Findings are checked against retrieved evidence.
Verification is performed for important results.
Evidence and source references are attached to findings.
A professional report is generated.
User can view/download the final deliverable.
Expected output:
Summary
Findings
Severity/status where applicable
Evidence
Source document
Page number where available
Recommendations
Verification information
Generated report
8. High-Level Architecture
USER | v FRONTEND (React Web App) | | REST API v BACKEND (FastAPI) | +----------+-----------+ |          |           | v          v           v AI/Model   RAG/       Agent/ Router     Multimodal  Workflow |          |           | +----------+-----------+ | v Controlled Tools Files / Search / Calculation | v Verification | v Deliverable Generation | v DOCX / XLSX / PPTX
9. Module Ownership
Module 1 — AI/LLM + Model Router
Owner: Member 1
Responsibilities:
Open-weight model integration
Model abstraction
Model registry
Model routing
Text generation
Reasoning model integration
Vision-language model integration where applicable
Model health/status information
Prompt templates
AI service interface
The rest of the application should not depend directly on a specific model. Models can be changed without requiring major changes to frontend or backend.
Module 2 — RAG + Multimodal Intelligence
Owner: Member 2
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
Owner: Member 3
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
Module 4 — Backend/API
Owner: Member 4
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
Module 5 — Frontend/UI
Owner: Member 5
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
The frontend communicates with the backend through defined APIs and must not directly depend on AI/RAG internal implementations.
Module 6 — Testing + Integration
Owner: Member 6
Responsibilities:
Unit testing support
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
Member 6 also acts as integration coordinator during development.
10. Development and Integration Principle
All six modules may be developed independently.
Shared interfaces must be defined before implementation.
Internal implementation may change freely within a module, but shared contracts should remain stable.
Frontend → Backend API → Agent/RAG/AI
The frontend should never depend on the internal code of AI, RAG, or Agent modules.
11. API Contracts
These are initial shared contracts. Changes must be documented before implementation.
11.1 Upload Document
POST /api/documents/upload
Request: multipart/form-data
file
Response: { "document_id": "doc_001", "filename": "Safety_Manual.pdf", "status": "processing" }
11.2 Get Document Status
GET /api/documents/{document_id}
Response: { "document_id": "doc_001", "filename": "Safety_Manual.pdf", "status": "completed" }
Possible statuses:
uploaded
processing
completed
failed
11.3 Create Task
POST /api/tasks
Request: { "message": "Audit this equipment against the safety standard.", "document_ids": ["doc_001", "doc_002"] }
Response: { "task_id": "task_001", "status": "queued" }
11.4 Get Task Status
GET /api/tasks/{task_id}
Response: { "task_id": "task_001", "status": "completed", "answer": "Three potential deviations were identified.", "confidence": 0.92, "sources": [ { "document_id": "doc_001", "filename": "Safety_Manual.pdf", "page": 17, "reference": "Relevant safety requirement..." } ], "findings": [], "report_id": "report_001" }
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
Request: { "query": "Applicable safety requirements", "document_ids": ["doc_001"], "top_k": 5 }
Response: { "results": [ { "document_id": "doc_001", "filename": "Safety_Manual.pdf", "page": 17, "text": "Relevant document content...", "score": 0.91 } ] }
11.6 AI Generation
POST /api/ai/generate
Request: { "task_type": "reasoning", "prompt": "Analyze the retrieved evidence.", "context": [] }
Response: { "model": "selected-model", "answer": "...", "confidence": 0.90 }
The model router internally selects the appropriate available model.
11.7 Generate Report
POST /api/reports/generate
Request: { "task_id": "task_001", "format": "docx" }
Response: { "report_id": "report_001", "status": "generated", "filename": "industrial_audit_report.docx" }
Supported formats may expand later.
12. Data Storage
The system requires three main storage categories.
12.1 Application Metadata
A relational database will store:
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
Safety_Manual.pdf | v Controlled File Storage | v document_id = doc_001
The database stores metadata associated with the document.
12.3 Vector Storage
Document information will be indexed for retrieval.
Document | v Parser | v Text/Image Extraction | v Chunking | v Embeddings | v Vector Database
13. RAG Flow
User Question | v Query Processing | v Embedding | v Vector Search | v Relevant Chunks | v Evidence Context | v LLM | v Grounded Answer
Retrieved information should preserve:
Document ID
Filename
Page number where available
Extracted text
Relevance score
14. Agent Flow
User Task | v Task Understanding | v Task Planning | v Select Required Actions | +--> RAG Search +--> Vision Analysis +--> Document Reading +--> Calculation Tool +--> AI Model +--> Report Generation | v Verification | v Final Findings | v Deliverable
The agent must not have unrestricted access to the operating system.
15. Verification Layer
The system should attempt to verify important outputs before presenting them as final findings.
Verification can include:
Checking whether claims have supporting sources
Comparing findings against retrieved requirements
Re-running calculations
Checking calculation consistency
Detecting unsupported claims
Checking missing evidence
Reporting uncertainty
The system must not present an uncertain AI-generated claim as a confirmed industrial fact.
Where verification cannot be completed, the result should clearly indicate uncertainty or require human review.
16. Evidence and Grounding
Important findings should provide evidence.
Example:
Finding: Potential safety requirement mismatch
Source: Safety_Manual.pdf
Page: 17
Evidence: Relevant requirement text
Observed Evidence: P&ID.pdf
Page: 4
Status: Requires review
Evidence should be traceable back to uploaded documents wherever technically possible.
17. Deliverable Generation
The system should generate actual work products.
Potential outputs:
DOCX reports
XLSX calculations
PPTX presentations
Structured summaries
Analysis results
Code files where applicable
The primary demonstration should prioritize a professional audit/approval report.
18. Security and Confidentiality
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
19. Technology Selection Principle
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
The exact technology stack will be finalized before implementation.
20. Development Environment
The initial development environment will be local.
AWS or another cloud platform is NOT a core development dependency.
The architecture should remain deployment-friendly so that private/cloud deployment can be added later without redesigning the core application.
21. Suggested Repository Structure
sih26117-sovereign-industrial-ai/ | ├── frontend/ ├── backend/ ├── ai/ ├── rag/ ├── agent/ ├── integration-tests/ ├── docs/ ├── data/ ├── PROJECT_SPEC.md ├── README.md └── docker-compose.yml
The exact structure may be adjusted after technology selection.
22. Git Workflow
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
Each member works primarily on their assigned branch/module.
Commit frequently with meaningful messages.
Test before creating a pull request.
Pull requests should be reviewed before merging.
Do not overwrite another member's work.
Resolve architectural conflicts before implementation.
Keep commits focused.
23. Change Management
Ideas from team members are encouraged.
Shared architecture changes must follow:
Idea | v Discuss | v Check impact | v Approve / Reject | v Update PROJECT_SPEC.md | v Implement
Changes that can normally be made independently:
Internal functions
UI styling
Component organization inside the assigned module
Internal implementation details
Refactoring within the module
Changes requiring team discussion:
API request/response formats
Database schema
Shared data models
Model interfaces
Agent-tool interfaces
Authentication architecture
Repository structure
Core workflow
24. AI Coding Tool Rule
All team members may use AI coding assistants.
Before making changes, every AI coding assistant must be instructed:
"Read PROJECT_SPEC.md before making changes. You are responsible for your assigned module. Follow the defined architecture and API contracts. Do not modify another module unnecessarily. Do not change shared interfaces without team approval."
AI-generated code must be reviewed and tested by the responsible team member.
25. Testing Strategy
Testing will happen continuously.
Level 1 — Unit Testing
Test individual functions/components.
Level 2 — API Testing
Test request/response contracts.
Level 3 — Module Integration
Test:
Backend ↔ AI
Backend ↔ RAG
Backend ↔ Agent
Level 4 — End-to-End
Test:
Upload → Process → Ask Task → Plan → Retrieve → Analyze → Verify → Generate Report → Download
Level 5 — Demo Validation
Run the exact final demonstration multiple times using a fixed test dataset.
26. Primary Success Criteria
The prototype should successfully demonstrate:
Required:
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
Strongly desired:
Interactive task progress
Multiple model support
Confidence/uncertainty indicators
Audit trail
Industrial-focused UI
Multiple deliverable formats
Local deployment using containers
27. Scope Control
The project should prioritize a strong end-to-end workflow over a large number of disconnected features.
First make this pipeline work:
Upload Document ↓ Process ↓ RAG ↓ AI ↓ Agent ↓ Verification ↓ Report
Only after this works should additional features be added.
28. Future Extensions
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
These are not required for the initial prototype unless time permits.
29. Definition of Done
A module is considered complete only when:
Its core functionality works.
It follows the agreed interface.
It has basic tests.
It does not break other modules.
Documentation is provided where necessary.
It can be integrated with the rest of the system.
The complete project is ready for demonstration only when the primary end-to-end workflow works reliably.
30. Final Product Vision
The final product should demonstrate:
"A sovereign industrial AI worker that can securely understand confidential multimodal information, plan and execute industrial knowledge tasks using appropriate local AI models and controlled tools, verify important results with evidence, and produce useful professional deliverables within the organization's controlled environment."
The product should be presented as an:
Industrial AI Workbench
not merely as a chatbot.
