import React from "react";
import { Outlet } from "react-router-dom";
import WebsiteNavbar from "./WebsiteNavbar";
import WebsiteFooter from "./WebsiteFooter";

export default function WebsiteLayout() {
  return (
    <div className="website-shell">
      <WebsiteNavbar />
      <main>
        <Outlet />
      </main>
      <WebsiteFooter />
    </div>
  );
}