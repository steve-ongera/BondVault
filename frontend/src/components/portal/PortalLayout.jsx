import React from "react";
import { Outlet } from "react-router-dom";
import PortalNavbar from "./PortalNavbar";
import PortalFooter from "./PortalFooter";

export default function PortalLayout() {
  return (
    <div className="app-shell">
      <PortalNavbar />
      <main className="app-content">
        <Outlet />
      </main>
      <PortalFooter />
    </div>
  );
}