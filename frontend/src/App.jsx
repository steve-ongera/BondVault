import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import { AuthProvider, useAuth } from "./context/AuthContext";

// Auth
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import KYCUpload from "./pages/auth/KYCUpload";

// Investor
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
import InvestmentCalculator from "./pages/tools/InvestmentCalculator";

// Advisor / Ops / Admin
import AdvisorDashboard from "./pages/advisor/AdvisorDashboard";
import OpsDashboard from "./pages/ops/OpsDashboard";
import KYCApprovalQueue from "./pages/ops/KYCApprovalQueue";
import AdminPanel from "./pages/admin/AdminPanel";
import AuditLogs from "./pages/admin/AuditLogs";

import NotFound from "./pages/NotFound";
import "./styles/main.css";

/**
 * Restricts a route to one or more roles. Redirects unauthenticated users
 * to /login and unauthorized users to their own dashboard.
 */
function ProtectedRoute({ children, roles }) {
  const { user, isLoading } = useAuth();

  if (isLoading) return <div className="page-loader">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />;

  return children;
}

function AppLayout() {
  const { user } = useAuth();

  return (
    <BrowserRouter>
      <div className="app-shell">
        <Navbar />

        <main className="app-content">
          <Routes>
            {/* Public */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Investor */}
            <Route path="/" element={
              <ProtectedRoute roles={["INVESTOR"]}><InvestorDashboard /></ProtectedRoute>
            } />
            <Route path="/kyc" element={
              <ProtectedRoute roles={["INVESTOR"]}><KYCUpload /></ProtectedRoute>
            } />
            <Route path="/bonds" element={
              <ProtectedRoute roles={["INVESTOR"]}><BondMarketplace /></ProtectedRoute>
            } />
            <Route path="/treasury-bills" element={
              <ProtectedRoute roles={["INVESTOR"]}><TreasuryBillsMarketplace /></ProtectedRoute>
            } />
            <Route path="/bonds/:id" element={
              <ProtectedRoute roles={["INVESTOR"]}><BondDetails /></ProtectedRoute>
            } />
            <Route path="/auctions" element={
              <ProtectedRoute roles={["INVESTOR"]}><BondAuctions /></ProtectedRoute>
            } />
            <Route path="/portfolio" element={
              <ProtectedRoute roles={["INVESTOR"]}><Portfolio /></ProtectedRoute>
            } />
            <Route path="/wallet" element={
              <ProtectedRoute roles={["INVESTOR"]}><Wallet /></ProtectedRoute>
            } />
            <Route path="/secondary-market" element={
              <ProtectedRoute roles={["INVESTOR"]}><SecondaryMarket /></ProtectedRoute>
            } />
            <Route path="/reinvestment" element={
              <ProtectedRoute roles={["INVESTOR"]}><ReinvestmentSettings /></ProtectedRoute>
            } />
            <Route path="/documents" element={
              <ProtectedRoute roles={["INVESTOR"]}><DocumentVault /></ProtectedRoute>
            } />
            <Route path="/tax-statements" element={
              <ProtectedRoute roles={["INVESTOR"]}><TaxStatements /></ProtectedRoute>
            } />
            <Route path="/calculator" element={<InvestmentCalculator />} />

            {/* Advisor */}
            <Route path="/advisor" element={
              <ProtectedRoute roles={["ADVISOR"]}><AdvisorDashboard /></ProtectedRoute>
            } />

            {/* Operations */}
            <Route path="/ops" element={
              <ProtectedRoute roles={["OPS", "ADMIN"]}><OpsDashboard /></ProtectedRoute>
            } />
            <Route path="/ops/kyc-queue" element={
              <ProtectedRoute roles={["OPS", "ADMIN"]}><KYCApprovalQueue /></ProtectedRoute>
            } />

            {/* Super Admin */}
            <Route path="/admin" element={
              <ProtectedRoute roles={["ADMIN"]}><AdminPanel /></ProtectedRoute>
            } />
            <Route path="/admin/audit-logs" element={
              <ProtectedRoute roles={["ADMIN"]}><AuditLogs /></ProtectedRoute>
            } />

            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>

        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppLayout />
    </AuthProvider>
  );
}