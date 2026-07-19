import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import AdminPanel from "../../pages/admin/AdminPanel";

/**
 * Renders at the /admin index route. ADMIN sees the panel directly;
 * OPS and ADVISOR get sent to their own landing page inside the same portal.
 */
export default function AdminPortalHome() {
  const { user } = useAuth();

  if (user?.role === "OPS") return <Navigate to="/admin/ops" replace />;
  if (user?.role === "ADVISOR") return <Navigate to="/admin/advisor" replace />;

  return <AdminPanel />;
}