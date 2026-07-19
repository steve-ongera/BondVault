import React from "react";
import { Link } from "react-router-dom";

export default function WebsiteFooter() {
  return (
    <>
      <div className="container-fluid bg-dark text-light footer mt-5 py-5 wow fadeIn" data-wow-delay="0.1s">
        <div className="container py-5">
          <div className="row g-5">
            <div className="col-lg-3 col-md-6">
              <h4 className="text-white mb-4">Our Office</h4>
              <p className="mb-2"><i className="fa fa-map-marker-alt me-3"></i>Nairobi, Kenya</p>
              <p className="mb-2"><i className="fa fa-phone-alt me-3"></i>+254 700 000000</p>
              <p className="mb-2"><i className="fa fa-envelope me-3"></i>support@example.com</p>
              <div className="d-flex pt-2">
                <a className="btn btn-square btn-outline-light rounded-circle me-2" href=""><i className="fab fa-twitter"></i></a>
                <a className="btn btn-square btn-outline-light rounded-circle me-2" href=""><i className="fab fa-facebook-f"></i></a>
                <a className="btn btn-square btn-outline-light rounded-circle me-2" href=""><i className="fab fa-youtube"></i></a>
                <a className="btn btn-square btn-outline-light rounded-circle me-2" href=""><i className="fab fa-linkedin-in"></i></a>
              </div>
            </div>
            <div className="col-lg-3 col-md-6">
              <h4 className="text-white mb-4">Services</h4>
              <Link className="btn btn-link" to="/services">Government Bonds</Link>
              <Link className="btn btn-link" to="/services">Treasury Bills</Link>
              <Link className="btn btn-link" to="/services">Infrastructure Bonds</Link>
              <Link className="btn btn-link" to="/calculator">Investment Calculator</Link>
            </div>
            <div className="col-lg-3 col-md-6">
              <h4 className="text-white mb-4">Quick Links</h4>
              <Link className="btn btn-link" to="/about">About Us</Link>
              <Link className="btn btn-link" to="/contact">Contact Us</Link>
              <Link className="btn btn-link" to="/register">Open An Account</Link>
              <Link className="btn btn-link" to="/login">Investor Login</Link>
            </div>
            <div className="col-lg-3 col-md-6">
              <h4 className="text-white mb-4">Newsletter</h4>
              <p>Get market updates and new auction alerts.</p>
              <div className="position-relative w-100">
                <input className="form-control bg-white border-0 w-100 py-3 ps-4 pe-5" type="text" placeholder="Your email" />
                <button type="button" className="btn btn-primary py-2 position-absolute top-0 end-0 mt-2 me-2">SignUp</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container-fluid copyright py-4">
        <div className="container">
          <div className="row">
            <div className="col-md-6 text-center text-md-start mb-3 mb-md-0">
              &copy; <a className="border-bottom" href="#">Finanza</a>, All Right Reserved.
            </div>
            <div className="col-md-6 text-center text-md-end">
              Built for the Kenyan bond &amp; T-bill market
            </div>
          </div>
        </div>
      </div>

      <a href="#" className="btn btn-lg btn-primary btn-lg-square rounded-circle back-to-top">
        <i className="bi bi-arrow-up"></i>
      </a>
    </>
  );
}