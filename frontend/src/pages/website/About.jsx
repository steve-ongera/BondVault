import React from "react";
import PageHeader from "../../components/PageHeader";

export default function About() {
  return (
    <>
      <PageHeader title="About" crumbs={[{ label: "About" }]} />

      <div className="container-xxl py-5">
        <div className="container">
          <div className="row g-4 align-items-end mb-4">
            <div className="col-lg-6 wow fadeInUp" data-wow-delay="0.1s">
              <div className="bg-light rounded" style={{ minHeight: 350 }}></div>
            </div>
            <div className="col-lg-6 wow fadeInUp" data-wow-delay="0.3s">
              <p className="d-inline-block border rounded text-primary fw-semi-bold py-1 px-3">About Us</p>
              <h1 className="display-5 mb-4">Making Government Securities Accessible To Everyone</h1>
              <p className="mb-4">
                Finanza was built to close the gap between everyday savers and the Central Bank of Kenya's
                bond and T-bill auctions. Instead of walking into a bank branch or CBK office with paperwork,
                investors can browse live offers, invest via M-Pesa, and track everything from their phone.
              </p>
              <div className="border rounded p-4">
                <nav>
                  <div className="nav nav-tabs mb-3" id="nav-tab" role="tablist">
                    <button className="nav-link fw-semi-bold active" id="nav-story-tab" data-bs-toggle="tab" data-bs-target="#nav-story" type="button" role="tab">Story</button>
                    <button className="nav-link fw-semi-bold" id="nav-mission-tab" data-bs-toggle="tab" data-bs-target="#nav-mission" type="button" role="tab">Mission</button>
                    <button className="nav-link fw-semi-bold" id="nav-vision-tab" data-bs-toggle="tab" data-bs-target="#nav-vision" type="button" role="tab">Vision</button>
                  </div>
                </nav>
                <div className="tab-content" id="nav-tabContent">
                  <div className="tab-pane fade show active" id="nav-story" role="tabpanel">
                    <p className="mb-0">
                      We started Finanza after seeing how few Kenyans outside institutional investors held
                      government debt directly, despite it being one of the safest returns available locally.
                    </p>
                  </div>
                  <div className="tab-pane fade" id="nav-mission" role="tabpanel">
                    <p className="mb-0">
                      Give every Kenyan with a phone and a bank or M-Pesa account a direct, transparent way
                      to invest in bonds and treasury bills.
                    </p>
                  </div>
                  <div className="tab-pane fade" id="nav-vision" role="tabpanel">
                    <p className="mb-0">
                      A country where saving in government securities is as normal and as easy as saving
                      in a bank account.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="border rounded p-4 wow fadeInUp" data-wow-delay="0.1s">
            <div className="row g-4">
              <div className="col-lg-4 wow fadeIn" data-wow-delay="0.1s">
                <div className="h-100">
                  <div className="d-flex">
                    <div className="flex-shrink-0 btn-lg-square rounded-circle bg-primary">
                      <i className="fa fa-shield-alt text-white"></i>
                    </div>
                    <div className="ps-3">
                      <h4>CBK-Backed Securities</h4>
                      <span>Every bond and bill listed is issued directly by the Central Bank of Kenya</span>
                    </div>
                    <div className="border-end d-none d-lg-block"></div>
                  </div>
                  <div className="border-bottom mt-4 d-block d-lg-none"></div>
                </div>
              </div>
              <div className="col-lg-4 wow fadeIn" data-wow-delay="0.3s">
                <div className="h-100">
                  <div className="d-flex">
                    <div className="flex-shrink-0 btn-lg-square rounded-circle bg-primary">
                      <i className="fa fa-user-check text-white"></i>
                    </div>
                    <div className="ps-3">
                      <h4>Verified Investors Only</h4>
                      <span>KYC checks on every account keep the platform compliant and secure</span>
                    </div>
                    <div className="border-end d-none d-lg-block"></div>
                  </div>
                  <div className="border-bottom mt-4 d-block d-lg-none"></div>
                </div>
              </div>
              <div className="col-lg-4 wow fadeIn" data-wow-delay="0.5s">
                <div className="h-100">
                  <div className="d-flex">
                    <div className="flex-shrink-0 btn-lg-square rounded-circle bg-primary">
                      <i className="fa fa-mobile-alt text-white"></i>
                    </div>
                    <div className="ps-3">
                      <h4>M-Pesa Native</h4>
                      <span>Deposit, withdraw and receive coupon payments without leaving M-Pesa</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}