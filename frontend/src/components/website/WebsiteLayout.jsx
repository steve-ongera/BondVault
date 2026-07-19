import React from "react";
import { NavLink, Link } from "react-router-dom";

const linkClass = ({ isActive }) => "nav-item nav-link" + (isActive ? " active" : "");

export default function WebsiteNavbar() {
  return (
    <div className="container-fluid fixed-top px-0 wow fadeIn" data-wow-delay="0.1s">
      <div className="top-bar row gx-0 align-items-center d-none d-lg-flex">
        <div className="col-lg-6 px-5 text-start">
          <small><i className="fa fa-shield-alt text-primary me-2"></i>Regulated Bond & T-Bill Investing</small>
          <small className="ms-4"><i className="fa fa-clock text-primary me-2"></i>Mon - Fri, 9am - 5pm</small>
        </div>
        <div className="col-lg-6 px-5 text-end">
          <small><i className="fa fa-envelope text-primary me-2"></i>support@example.com</small>
          <small className="ms-4"><i className="fa fa-phone-alt text-primary me-2"></i>+254 700 000000</small>
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
            <NavLink to="/" end className={linkClass}>Home</NavLink>
            <NavLink to="/about" className={linkClass}>About</NavLink>
            <NavLink to="/services" className={linkClass}>Services</NavLink>
            <NavLink to="/calculator" className={linkClass}>Calculator</NavLink>
            <NavLink to="/contact" className={linkClass}>Contact</NavLink>
          </div>
          <div className="d-none d-lg-flex ms-2">
            <Link to="/login" className="btn btn-outline-primary py-2 px-4 me-2">Login</Link>
            <Link to="/register" className="btn btn-primary py-2 px-4">Get Started</Link>
          </div>
        </div>
      </nav>
    </div>
  );
}