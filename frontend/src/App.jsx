import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import { AuthProvider, useAuth } from "./context/AuthContext";

// Layouts
import WebsiteLayout from "./components/website/WebsiteLayout";
import PortalLayout from "./components/portal/PortalLayout";
import AdminPortalHome from "./components/portal/AdminPortalHome";

// Website (public)
import Home from "./pages/website/Home";
import About from "./pages/website/About";
import Services from "./pages/website/Services";
import Contact from "./pages/website/Contact";
import InvestmentCalculator from "./pages/website/InvestmentCalculator";

// Auth (public, rendered inside the website layout)
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import KYCUpload from "./pages/auth/KYCUpload";

// User Portal
import InvestorDashboard from "./pages/dashboard/InvestorDashboard";
import BondMarketplace from "./pages/marketplace/BondMarketplace";
import TreasuryBillsMarketplace from "./pages/marketplace/TreasuryBillsMarketplace";
import BondDetails from "./pages/marketplace/BondDetails";
import BondAuctions from "./pages/marketplace/BondAuctions";
import Portfolio from "./pages/portfolio/Portfolio";
import Wallet from "./pages/wallet/Wallet";
import SecondaryMarket from "./pages/trading/SecondaryMarket";
import ReinvestmentSettings from "./pages/reinvestment/ReinvestmentSettings";
import DocumentVault from "./pages/documents/DocumentVault";
import TaxStatements from "./pages/documents/TaxStatements";

// Admin Portal (Advisor / Ops / Admin)
import AdvisorDashboard from "./pages/advisor/AdvisorDashboard";
import OpsDashboard from "./pages/ops/OpsDashboard";
import KYCApprovalQueue from "./pages/ops/KYCApprovalQueue";
import AuditLogs from "./pages/admin/AuditLogs";

import NotFound from "./pages/NotFound";
import "./styles/main.css";

/**
 * Restricts a route to one or more roles. Redirects unauthenticated users
 * to /login and unauthorized users back to the public website.
 */
function ProtectedRoute({ children, roles }) {
  const { user, isLoading } = useAuth();

  if (isLoading) return <div className="page-loader">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />;

  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* ---------- Module 1: Public Website ---------- */}
          <Route element={<WebsiteLayout />}>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/services" element={<Services />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/calculator" element={<InvestmentCalculator />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Route>

          {/* ---------- Module 2: User Portal (investor) ---------- */}
          <Route
            path="/portal"
            element={
              <ProtectedRoute roles={["INVESTOR"]}>
                <PortalLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<InvestorDashboard />} />
            <Route path="kyc" element={<KYCUpload />} />
            <Route path="bonds" element={<BondMarketplace />} />
            <Route path="bonds/:id" element={<BondDetails />} />
            <Route path="treasury-bills" element={<TreasuryBillsMarketplace />} />
            <Route path="auctions" element={<BondAuctions />} />
            <Route path="portfolio" element={<Portfolio />} />
            <Route path="wallet" element={<Wallet />} />
            <Route path="secondary-market" element={<SecondaryMarket />} />
            <Route path="reinvestment" element={<ReinvestmentSettings />} />
            <Route path="documents" element={<DocumentVault />} />
            <Route path="tax-statements" element={<TaxStatements />} />
          </Route>

          {/* ---------- Module 3: Admin Portal (advisor / ops / admin) ---------- */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute roles={["ADVISOR", "OPS", "ADMIN"]}>
                <PortalLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<AdminPortalHome />} />
            <Route path="advisor" element={<ProtectedRoute roles={["ADVISOR"]}><AdvisorDashboard /></ProtectedRoute>} />
            <Route path="ops" element={<ProtectedRoute roles={["OPS", "ADMIN"]}><OpsDashboard /></ProtectedRoute>} />
            <Route path="ops/kyc-queue" element={<ProtectedRoute roles={["OPS", "ADMIN"]}><KYCApprovalQueue /></ProtectedRoute>} />
            <Route path="audit-logs" element={<ProtectedRoute roles={["ADMIN"]}><AuditLogs /></ProtectedRoute>} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}