import React from "react";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <>
      {/* Hero Start */}
      <div className="container-fluid p-0 mb-5 hero-offset wow fadeIn" data-wow-delay="0.1s">
        <div id="header-carousel" className="carousel slide carousel-fade" data-bs-ride="carousel">
          <div className="carousel-inner">
            <div className="carousel-item active">
              <div className="bg-light" style={{ minHeight: 550 }}></div>
              <div className="carousel-caption">
                <div className="container">
                  <div className="row justify-content-start">
                    <div className="col-lg-8">
                      <p className="d-inline-block border border-primary rounded text-primary fw-semi-bold py-1 px-3 animated slideInDown">
                        Government-Backed Investing
                      </p>
                      <h1 className="display-1 mb-4 animated slideInDown">
                        Grow Your Money With Kenyan Treasury Bonds & T-Bills
                      </h1>
                      <p className="mb-4" style={{ maxWidth: 600 }}>
                        Invest directly in CBK-issued bonds and treasury bills from as little as KES 50,000,
                        track everything in one wallet, and get paid straight to M-Pesa.
                      </p>
                      <Link to="/register" className="btn btn-primary py-3 px-5 animated slideInDown">
                        Start Investing
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="carousel-item">
              <div className="bg-light" style={{ minHeight: 550 }}></div>
              <div className="carousel-caption">
                <div className="container">
                  <div className="row justify-content-start">
                    <div className="col-lg-7">
                      <p className="d-inline-block border border-primary rounded text-primary fw-semi-bold py-1 px-3 animated slideInDown">
                        Live Auctions
                      </p>
                      <h1 className="display-1 mb-4 animated slideInDown">Bid On The Next CBK Auction</h1>
                      <Link to="/register" className="btn btn-primary py-3 px-5 animated slideInDown">
                        View Open Auctions
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <button className="carousel-control-prev" type="button" data-bs-target="#header-carousel" data-bs-slide="prev">
            <span className="carousel-control-prev-icon" aria-hidden="true"></span>
            <span className="visually-hidden">Previous</span>
          </button>
          <button className="carousel-control-next" type="button" data-bs-target="#header-carousel" data-bs-slide="next">
            <span className="carousel-control-next-icon" aria-hidden="true"></span>
            <span className="visually-hidden">Next</span>
          </button>
        </div>
      </div>
      {/* Hero End */}

      {/* About Start */}
      <div className="container-xxl py-5">
        <div className="container">
          <div className="row g-4 align-items-center">
            <div className="col-lg-6 wow fadeInUp" data-wow-delay="0.1s">
              <div className="bg-light rounded" style={{ minHeight: 350 }}></div>
            </div>
            <div className="col-lg-6 wow fadeInUp" data-wow-delay="0.3s">
              <p className="d-inline-block border rounded text-primary fw-semi-bold py-1 px-3">Why Finanza</p>
              <h1 className="display-5 mb-4">A Simpler Way Into Government Securities</h1>
              <p className="mb-4">
                Buying bonds and T-bills the traditional way means paperwork at a bank or CBK counter.
                Finanza moves the whole process online: browse what's on offer, invest via M-Pesa, and
                receive coupon payments and maturities straight into your wallet.
              </p>
              <div className="row g-3">
                <div className="col-sm-6"><p className="mb-0"><i className="fa fa-check text-primary me-3"></i>No paperwork or bank queues</p></div>
                <div className="col-sm-6"><p className="mb-0"><i className="fa fa-check text-primary me-3"></i>Minimum investment of KES 50,000</p></div>
                <div className="col-sm-6"><p className="mb-0"><i className="fa fa-check text-primary me-3"></i>M-Pesa deposits and payouts</p></div>
                <div className="col-sm-6"><p className="mb-0"><i className="fa fa-check text-primary me-3"></i>Auto-reinvestment at maturity</p></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* About End */}

      {/* Facts Start */}
      <div className="container-fluid facts my-5 py-5">
        <div className="container py-5">
          <div className="row g-5">
            <div className="col-sm-6 col-lg-3 text-center wow fadeIn" data-wow-delay="0.1s">
              <i className="fa fa-users fa-3x text-white mb-3"></i>
              <h1 className="display-4 text-white">4,800+</h1>
              <span className="fs-5 text-white">Registered Investors</span>
              <hr className="bg-white w-25 mx-auto mb-0" />
            </div>
            <div className="col-sm-6 col-lg-3 text-center wow fadeIn" data-wow-delay="0.3s">
              <i className="fa fa-file-invoice fa-3x text-white mb-3"></i>
              <h1 className="display-4 text-white">18</h1>
              <span className="fs-5 text-white">Bonds & T-Bills Listed</span>
              <hr className="bg-white w-25 mx-auto mb-0" />
            </div>
            <div className="col-sm-6 col-lg-3 text-center wow fadeIn" data-wow-delay="0.5s">
              <i className="fa fa-wallet fa-3x text-white mb-3"></i>
              <h1 className="display-4 text-white">KES 340M+</h1>
              <span className="fs-5 text-white">Invested Through The Platform</span>
              <hr className="bg-white w-25 mx-auto mb-0" />
            </div>
            <div className="col-sm-6 col-lg-3 text-center wow fadeIn" data-wow-delay="0.7s">
              <i className="fa fa-shield-alt fa-3x text-white mb-3"></i>
              <h1 className="display-4 text-white">100%</h1>
              <span className="fs-5 text-white">CBK-Backed Securities</span>
              <hr className="bg-white w-25 mx-auto mb-0" />
            </div>
          </div>
        </div>
      </div>
      {/* Facts End */}

      {/* Services Teaser Start */}
      <div className="container-xxl py-5">
        <div className="container">
          <div className="text-center mx-auto wow fadeInUp" data-wow-delay="0.1s" style={{ maxWidth: 600 }}>
            <p className="d-inline-block border rounded text-primary fw-semi-bold py-1 px-3">What You Can Invest In</p>
            <h1 className="display-5 mb-5">Bonds, Bills And Auctions In One Place</h1>
          </div>
          <div className="row g-4">
            <div className="col-lg-4 wow fadeIn" data-wow-delay="0.1s">
              <div className="feature-box border rounded p-4 h-100">
                <i className="fa fa-chart-line fa-3x text-primary mb-3"></i>
                <h4 className="mb-3">Fixed & Infrastructure Bonds</h4>
                <p className="mb-3">Multi-year bonds with semi-annual coupon payments, including tax-free infrastructure bonds.</p>
                <Link className="fw-semi-bold" to="/services">Read More <i className="fa fa-arrow-right ms-1"></i></Link>
              </div>
            </div>
            <div className="col-lg-4 wow fadeIn" data-wow-delay="0.3s">
              <div className="feature-box border rounded p-4 h-100">
                <i className="fa fa-receipt fa-3x text-primary mb-3"></i>
                <h4 className="mb-3">Treasury Bills</h4>
                <p className="mb-3">91, 182 and 364-day bills for short-term, low-risk returns on idle cash.</p>
                <Link className="fw-semi-bold" to="/services">Read More <i className="fa fa-arrow-right ms-1"></i></Link>
              </div>
            </div>
            <div className="col-lg-4 wow fadeIn" data-wow-delay="0.5s">
              <div className="feature-box border rounded p-4 h-100">
                <i className="fa fa-gavel fa-3x text-primary mb-3"></i>
                <h4 className="mb-3">Live CBK Auctions</h4>
                <p className="mb-3">Place competitive or non-competitive bids on new issues before the auction closes.</p>
                <Link className="fw-semi-bold" to="/services">Read More <i className="fa fa-arrow-right ms-1"></i></Link>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* Services Teaser End */}

      {/* CTA Start */}
      <div className="container-fluid callback my-5 pt-5">
        <div className="container pt-5">
          <div className="row justify-content-center">
            <div className="col-lg-7 text-center">
              <div className="bg-white border rounded p-4 p-sm-5 wow fadeInUp" data-wow-delay="0.5s">
                <p className="d-inline-block border rounded text-primary fw-semi-bold py-1 px-3">Get In Touch</p>
                <h1 className="display-5 mb-4">Open A Free Investor Account</h1>
                <p className="mb-4">Registration takes a few minutes. KYC approval is usually done within 1–2 business days.</p>
                <Link to="/register" className="btn btn-primary py-3 px-5 me-2">Create Account</Link>
                <Link to="/calculator" className="btn btn-outline-primary py-3 px-5">Try The Calculator</Link>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* CTA End */}
    </>
  );
}