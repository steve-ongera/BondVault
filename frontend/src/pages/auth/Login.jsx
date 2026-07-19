import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const roleLandingPage = (role) => {
    if (role === "INVESTOR") return "/portal";
    if (role === "ADVISOR") return "/admin/advisor";
    if (role === "OPS") return "/admin/ops";
    if (role === "ADMIN") return "/admin";
    return "/";
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      // TODO: wire to POST /api/auth/login — assumes login() resolves with the logged-in user
      const loggedInUser = await login(form);
      navigate(roleLandingPage(loggedInUser?.role));
    } catch (err) {
      setError("Could not sign in. Check your email and password.");
    }
  };

  return (
    <div className="container-fluid callback my-5 pt-5">
      <div className="container pt-5">
        <div className="row justify-content-center">
          <div className="col-lg-6">
            <div className="bg-white border rounded p-4 p-sm-5 wow fadeInUp" data-wow-delay="0.5s">
              <div className="text-center mx-auto mb-4" style={{ maxWidth: 400 }}>
                <p className="d-inline-block border rounded text-primary fw-semi-bold py-1 px-3">Welcome Back</p>
                <h1 className="display-5 mb-0">Sign In To Your Account</h1>
              </div>

              {error && <div className="alert alert-danger">{error}</div>}

              <form onSubmit={onSubmit}>
                <div className="row g-3">
                  <div className="col-12">
                    <div className="form-floating">
                      <input
                        type="email"
                        name="email"
                        className="form-control"
                        id="email"
                        placeholder="Your Email"
                        value={form.email}
                        onChange={onChange}
                        required
                      />
                      <label htmlFor="email">Your Email</label>
                    </div>
                  </div>
                  <div className="col-12">
                    <div className="form-floating">
                      <input
                        type="password"
                        name="password"
                        className="form-control"
                        id="password"
                        placeholder="Password"
                        value={form.password}
                        onChange={onChange}
                        required
                      />
                      <label htmlFor="password">Password</label>
                    </div>
                  </div>
                  <div className="col-12 text-center">
                    <button className="btn btn-primary w-100 py-3" type="submit">Sign In</button>
                  </div>
                  <div className="col-12 text-center">
                    <span>Don't have an account? </span>
                    <Link to="/register" className="fw-semi-bold">Register here</Link>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}