import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Workspace from "./pages/Workspace";
import Documents from "./pages/Documents";
import Deliverables from "./pages/Deliverables";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/workspace" element={<Workspace />} />
      <Route path="/documents" element={<Documents />} />
      <Route path="/deliverables" element={<Deliverables />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
