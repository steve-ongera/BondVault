import React from "react";
import { NavLink, Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

const linkClass = ({ isActive }) => "nav-item nav-link" + (isActive ? " active" : "");

export default function PortalNavbar() {
  const { user, logout } = useAuth();

  return (
    <div className="container-fluid fixed-top px-0 wow fadeIn" data-wow-delay="0.1s">
      <div className="top-bar row gx-0 align-items-center d-none d-lg-flex">
        <div className="col-lg-6 px-5 text-start">
          <Link to="/" className="text-decoration-none">
            <small><i className="fa fa-arrow-left text-primary me-2"></i>Back to Website</small>
          </Link>
        </div>
        <div className="col-lg-6 px-5 text-end">
          <small><i className="fa fa-user text-primary me-2"></i>{user?.fullName || user?.email}</small>
        </div>
      </div>

      <nav className="navbar navbar-expand-lg navbar-light py-lg-0 px-lg-5 wow fadeIn" data-wow-delay="0.1s">
        <Link to="/" className="navbar-brand ms-4 ms-lg-0">
          <h1 className="display-5 text-primary m-0">Finanza</h1>
        </Link>
        <button
          type="button"
          className="navbar-toggler me-4"
          data-bs-toggle="collapse"
          data-bs-target="#navbarCollapse"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarCollapse">
          <div className="navbar-nav ms-auto p-4 p-lg-0">
            {user?.role === "INVESTOR" && (
              <>
                <NavLink to="/portal" end className={linkClass}>Dashboard</NavLink>
                <NavLink to="/portal/bonds" className={linkClass}>Bonds</NavLink>
                <NavLink to="/portal/treasury-bills" className={linkClass}>T-Bills</NavLink>
                <NavLink to="/portal/auctions" className={linkClass}>Auctions</NavLink>
                <div className="nav-item dropdown">
                  <a href="#" className="nav-link dropdown-toggle" data-bs-toggle="dropdown">Portfolio</a>
                  <div className="dropdown-menu border-light m-0">
                    <NavLink to="/portal/portfolio" className="dropdown-item">My Portfolio</NavLink>
                    <NavLink to="/portal/wallet" className="dropdown-item">Wallet</NavLink>
                    <NavLink to="/portal/secondary-market" className="dropdown-item">Secondary Market</NavLink>
                    <NavLink to="/portal/reinvestment" className="dropdown-item">Reinvestment</NavLink>
                    <NavLink to="/portal/documents" className="dropdown-item">Document Vault</NavLink>
                    <NavLink to="/portal/tax-statements" className="dropdown-item">Tax Statements</NavLink>
                  </div>
                </div>
              </>
            )}

            {user?.role === "ADVISOR" && (
              <NavLink to="/admin/advisor" className={linkClass}>Advisor Dashboard</NavLink>
            )}

            {(user?.role === "OPS" || user?.role === "ADMIN") && (
              <div className="nav-item dropdown">
                <a href="#" className="nav-link dropdown-toggle" data-bs-toggle="dropdown">Operations</a>
                <div className="dropdown-menu border-light m-0">
                  <NavLink to="/admin/ops" className="dropdown-item">Ops Dashboard</NavLink>
                  <NavLink to="/admin/ops/kyc-queue" className="dropdown-item">KYC Queue</NavLink>
                </div>
              </div>
            )}

            {user?.role === "ADMIN" && (
              <div className="nav-item dropdown">
                <a href="#" className="nav-link dropdown-toggle" data-bs-toggle="dropdown">Admin</a>
                <div className="dropdown-menu border-light m-0">
                  <NavLink to="/admin" end className="dropdown-item">Admin Panel</NavLink>
                  <NavLink to="/admin/audit-logs" className="dropdown-item">Audit Logs</NavLink>
                </div>
              </div>
            )}
          </div>

          {user && (
            <div className="d-none d-lg-flex ms-2">
              <button onClick={logout} className="btn btn-primary py-2 px-4">
                Logout
              </button>
            </div>
          )}
        </div>
      </nav>
    </div>
  );
}