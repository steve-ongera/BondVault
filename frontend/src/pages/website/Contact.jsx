import React, { useState } from "react";
import PageHeader from "../../components/PageHeader";

export default function Contact() {
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [sent, setSent] = useState(false);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = (e) => {
    e.preventDefault();
    // TODO: wire to POST /api/contact
    setSent(true);
  };

  return (
    <>
      <PageHeader title="Contact" crumbs={[{ label: "Contact" }]} />

      <div className="container-xxl py-5">
        <div className="container">
          <div className="row g-5">
            <div className="col-lg-6 wow fadeIn" data-wow-delay="0.1s">
              <p className="d-inline-block border rounded text-primary fw-semi-bold py-1 px-3">Contact</p>
              <h1 className="display-5 mb-4">Questions About Investing? Talk To Us</h1>
              <p className="mb-4">
                Reach out about account setup, KYC status, or a specific bond or T-bill auction and
                we'll get back to you within one business day.
              </p>

              {sent && <div className="alert alert-success">Thanks — your message has been sent.</div>}

              <form onSubmit={onSubmit}>
                <div className="row g-3">
                  <div className="col-md-6">
                    <div className="form-floating">
                      <input type="text" name="name" className="form-control" id="name" placeholder="Your Name" value={form.name} onChange={onChange} required />
                      <label htmlFor="name">Your Name</label>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="form-floating">
                      <input type="email" name="email" className="form-control" id="email" placeholder="Your Email" value={form.email} onChange={onChange} required />
                      <label htmlFor="email">Your Email</label>
                    </div>
                  </div>
                  <div className="col-12">
                    <div className="form-floating">
                      <input type="text" name="subject" className="form-control" id="subject" placeholder="Subject" value={form.subject} onChange={onChange} required />
                      <label htmlFor="subject">Subject</label>
                    </div>
                  </div>
                  <div className="col-12">
                    <div className="form-floating">
                      <textarea
                        className="form-control"
                        placeholder="Leave a message here"
                        id="message"
                        name="message"
                        style={{ height: 100 }}
                        value={form.message}
                        onChange={onChange}
                        required
                      ></textarea>
                      <label htmlFor="message">Message</label>
                    </div>
                  </div>
                  <div className="col-12">
                    <button className="btn btn-primary py-3 px-5" type="submit">Send Message</button>
                  </div>
                </div>
              </form>
            </div>
            <div className="col-lg-6 wow fadeIn" data-wow-delay="0.5s" style={{ minHeight: 450 }}>
              <div className="position-relative rounded overflow-hidden h-100 bg-light" style={{ minHeight: 450 }}>
                <iframe
                  className="position-relative w-100 h-100"
                  src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d63769.68!2d36.78!3d-1.286389!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x182f1172d84d49a5%3A0x738259ce540e3af9!2sNairobi!5e0!3m2!1sen!2ske!4v1603794290143!5m2!1sen!2ske"
                  style={{ minHeight: 450, border: 0 }}
                  loading="lazy"
                  title="Finanza Nairobi office map"
                ></iframe>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}