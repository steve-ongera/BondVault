import React from "react";
import { Link } from "react-router-dom";
import PageHeader from "../../components/PageHeader";

export default function Services() {
  return (
    <>
      <PageHeader title="Services" crumbs={[{ label: "Services" }]} />

      <div className="container-xxl py-5">
        <div className="container">
          <div className="text-center mx-auto wow fadeInUp" data-wow-delay="0.1s" style={{ maxWidth: 600 }}>
            <p className="d-inline-block border rounded text-primary fw-semi-bold py-1 px-3">Our Services</p>
            <h1 className="display-5 mb-5">Investment Products On Finanza</h1>
          </div>

          <div className="row g-4 wow fadeInUp" data-wow-delay="0.3s">
            <div className="col-lg-4">
              <div className="nav nav-pills d-flex justify-content-between w-100 h-100 me-4">
                <button className="nav-link w-100 d-flex align-items-center text-start border p-4 mb-4 active" data-bs-toggle="pill" data-bs-target="#tab-pane-1" type="button">
                  <h5 className="m-0"><i className="fa fa-chart-line text-primary me-3"></i>Fixed Rate Bonds</h5>
                </button>
                <button className="nav-link w-100 d-flex align-items-center text-start border p-4 mb-4" data-bs-toggle="pill" data-bs-target="#tab-pane-2" type="button">
                  <h5 className="m-0"><i className="fa fa-road text-primary me-3"></i>Infrastructure Bonds</h5>
                </button>
                <button className="nav-link w-100 d-flex align-items-center text-start border p-4 mb-4" data-bs-toggle="pill" data-bs-target="#tab-pane-3" type="button">
                  <h5 className="m-0"><i className="fa fa-receipt text-primary me-3"></i>Treasury Bills</h5>
                </button>
                <button className="nav-link w-100 d-flex align-items-center text-start border p-4 mb-0" data-bs-toggle="pill" data-bs-target="#tab-pane-4" type="button">
                  <h5 className="m-0"><i className="fa fa-gavel text-primary me-3"></i>Live Auctions</h5>
                </button>
              </div>
            </div>
            <div className="col-lg-8">
              <div className="tab-content w-100">
                <div className="tab-pane fade show active" id="tab-pane-1">
                  <h3 className="mb-4">Fixed Rate Treasury Bonds</h3>
                  <p className="mb-4">
                    Multi-year bonds issued by the National Treasury with a fixed coupon rate paid
                    semi-annually. Terms typically range from 2 to 25 years.
                  </p>
                  <p><i className="fa fa-check text-primary me-3"></i>Minimum investment: KES 50,000</p>
                  <p><i className="fa fa-check text-primary me-3"></i>Coupon paid every 6 months</p>
                  <p><i className="fa fa-check text-primary me-3"></i>Principal repaid at maturity</p>
                  <Link to="/register" className="btn btn-primary py-3 px-5 mt-3">Get Started</Link>
                </div>
                <div className="tab-pane fade" id="tab-pane-2">
                  <h3 className="mb-4">Infrastructure Bonds (IFB)</h3>
                  <p className="mb-4">
                    Bonds that fund specific government infrastructure projects, with interest income
                    exempt from withholding tax.
                  </p>
                  <p><i className="fa fa-check text-primary me-3"></i>Minimum investment: KES 50,000</p>
                  <p><i className="fa fa-check text-primary me-3"></i>Tax-free coupon income</p>
                  <p><i className="fa fa-check text-primary me-3"></i>Terms from 6 to 20+ years</p>
                  <Link to="/register" className="btn btn-primary py-3 px-5 mt-3">Get Started</Link>
                </div>
                <div className="tab-pane fade" id="tab-pane-3">
                  <h3 className="mb-4">Treasury Bills</h3>
                  <p className="mb-4">
                    Short-term, discounted instruments for parking cash for a few months at rates
                    typically ahead of a bank fixed deposit.
                  </p>
                  <p><i className="fa fa-check text-primary me-3"></i>91, 182 or 364-day tenors</p>
                  <p><i className="fa fa-check text-primary me-3"></i>Minimum investment: KES 50,000</p>
                  <p><i className="fa fa-check text-primary me-3"></i>Sold at a discount, paid at face value</p>
                  <Link to="/register" className="btn btn-primary py-3 px-5 mt-3">Get Started</Link>
                </div>
                <div className="tab-pane fade" id="tab-pane-4">
                  <h3 className="mb-4">Live CBK Auctions</h3>
                  <p className="mb-4">
                    Every new bond and bill issue goes through a CBK auction. Bid competitively with your
                    own rate, or non-competitively at the weighted average accepted rate.
                  </p>
                  <p><i className="fa fa-check text-primary me-3"></i>Real-time auction countdowns</p>
                  <p><i className="fa fa-check text-primary me-3"></i>Competitive & non-competitive bidding</p>
                  <p><i className="fa fa-check text-primary me-3"></i>Results reflected in your portfolio automatically</p>
                  <Link to="/register" className="btn btn-primary py-3 px-5 mt-3">Get Started</Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}