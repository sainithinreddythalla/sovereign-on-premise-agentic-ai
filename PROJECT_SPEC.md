# SIH26117 — Sovereign On-Premise Agentic AI Workbench

## 1. Project Goal

Build a sovereign, self-hosted AI workbench for confidential industrial knowledge work.

The system will allow organizations to process sensitive documents and industrial information within their controlled environment using open-weight multimodal AI models.

The platform should not behave like a simple chatbot. It should understand a task, plan the required steps, use approved tools and internal knowledge, verify important results, and generate useful deliverables.

---

## 2. Core Problem

Industrial organizations handle confidential information such as:

- Engineering drawings
- P&IDs
- Inspection reports
- Maintenance documents
- Internal standards and manuals
- Scanned documents
- Handwritten notes
- Photographs
- Financial and business documents
- Internal source code
- Vendor and project information

Existing public AI assistants may not be suitable for such confidential information because organizations need stronger control over where their data and AI processing occur.

Therefore, the project aims to provide AI capabilities while keeping sensitive processing within the organization's controlled environment.

---

## 3. Proposed Solution

We will build a Sovereign Industrial AI Workbench with the following capabilities:

1. Self-hosted/open-weight AI models
2. Multimodal document understanding
3. Retrieval-Augmented Generation (RAG)
4. Intelligent model routing
5. Agentic task planning and execution
6. Controlled local tools
7. Evidence-based answers
8. Result verification
9. Automatic deliverable generation
10. Security, access control and auditability

---

## 4. Core Principle

The system should follow:

Confidential Task
→ Understand
→ Plan
→ Retrieve
→ Select Model
→ Execute Tools
→ Verify
→ Generate Deliverable

The goal is to transform confidential information into a verified work product rather than simply generating a chat response.

---

## 5. Primary Demonstration Workflow

The primary demonstration will focus on a confidential industrial engineering/safety audit.

Example inputs:

- P&ID / engineering drawing
- Internal safety standard
- Inspection report
- Equipment photographs

Example user request:

"Audit this system against the applicable internal safety requirements, identify deviations with evidence, and prepare an approval/audit report."

Expected workflow:

1. Understand the user's task
2. Analyze uploaded documents and images
3. Retrieve relevant internal standards
4. Select appropriate AI models
5. Perform multi-step analysis
6. Execute calculations/tools when required
7. Identify findings and deviations
8. Provide evidence and source references
9. Verify important findings
10. Generate a professional report

Expected output:

- Findings
- Evidence/source references
- Recommendations
- Verification information
- Downloadable report

---

## 6. Project Differentiation

The project must NOT be positioned as:

- A generic chatbot
- A simple "Chat with PDF" application
- A basic RAG chatbot
- A simple private LLM interface

The project differentiation should focus on:

- Confidential industrial workflows
- Intelligent multi-model routing
- Multimodal industrial document understanding
- Agentic task execution
- Controlled tool usage
- Evidence and verification
- Actual work-product generation
- Sovereign/self-hosted deployment

---

## 7. Development Principle

The project will be developed as independent modules with clearly defined interfaces.

Each team member can develop their module independently, but shared interfaces and architecture must be agreed upon before implementation.

No member should independently change a shared API, database contract, or overall architecture without team agreement.

---

## 8. Team Rule

Before making code changes, every team member must:

1. Read this PROJECT_SPEC.md
2. Understand their assigned module
3. Follow the defined interfaces
4. Avoid modifying other modules unnecessarily
5. Test their module before integration
6. Communicate proposed architecture changes before implementing them

PROJECT_SPEC.md will act as the single source of truth for the project.
