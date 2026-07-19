import React from "react";
import { Link } from "react-router-dom";

export default function PortalFooter() {
  return (
    <div className="container-fluid copyright py-4 mt-5">
      <div className="container">
        <div className="row align-items-center">
          <div className="col-md-6 text-center text-md-start mb-3 mb-md-0">
            &copy; <Link className="border-bottom" to="/">Finanza</Link>, All Right Reserved.
          </div>
          <div className="col-md-6 text-center text-md-end">
            <Link className="btn btn-link d-inline" to="/portal">Dashboard</Link>
            <Link className="btn btn-link d-inline" to="/contact">Support</Link>
          </div>
        </div>
      </div>
    </div>
  );
}