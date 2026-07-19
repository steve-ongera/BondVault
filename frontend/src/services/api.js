import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// ----------------------------------------------------------------------
// Attach JWT access token to every request
// ----------------------------------------------------------------------
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ----------------------------------------------------------------------
// Auto-refresh access token on 401, retry the original request once
// ----------------------------------------------------------------------
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refresh = localStorage.getItem("refresh_token");
        const { data } = await axios.post(`${BASE_URL}/auth/refresh/`, { refresh });
        localStorage.setItem("access_token", data.access);
        originalRequest.headers.Authorization = `Bearer ${data.access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

// ======================================================================
// Auth
// ======================================================================
export const registerUser = (payload) => api.post("/auth/register/", payload);
export const loginUser = (payload) => api.post("/auth/login/", payload);
export const refreshToken = (refresh) => api.post("/auth/refresh/", { refresh });
export const getCurrentUser = () => api.get("/auth/me/");

// ======================================================================
// KYC
// ======================================================================
export const uploadKYCDocument = (formData) =>
  api.post("/kyc-documents/", formData, { headers: { "Content-Type": "multipart/form-data" } });
export const getKYCDocuments = () => api.get("/kyc-documents/");
export const reviewKYCDocument = (id, payload) => api.post(`/kyc-documents/${id}/review/`, payload);

// ======================================================================
// Investor profile & risk
// ======================================================================
export const getInvestorProfile = (id) => api.get(`/investor-profiles/${id}/`);
export const updateInvestorProfile = (id, payload) => api.patch(`/investor-profiles/${id}/`, payload);
export const submitRiskProfile = (payload) => api.post("/risk-profiles/", payload);

// ======================================================================
// Bank & mobile money accounts
// ======================================================================
export const getBankAccounts = () => api.get("/bank-accounts/");
export const addBankAccount = (payload) => api.post("/bank-accounts/", payload);
export const getMobileMoneyAccounts = () => api.get("/mobile-money-accounts/");
export const addMobileMoneyAccount = (payload) => api.post("/mobile-money-accounts/", payload);

// ======================================================================
// Wallet
// ======================================================================
export const getWallet = () => api.get("/wallet/");
export const depositToWallet = (payload) => api.post("/wallet/deposit/", payload);
export const withdrawFromWallet = (payload) => api.post("/wallet/withdraw/", payload);

// ======================================================================
// Marketplace — Bonds & Treasury Bills
// ======================================================================
export const getBonds = (params) => api.get("/securities/", { params: { instrument_type: "BOND", ...params } });
export const getTreasuryBills = (params) => api.get("/securities/", { params: { instrument_type: "TBILL", ...params } });
export const getSecurityById = (id) => api.get(`/securities/${id}/`);
export const getAuctions = () => api.get("/auctions/");

// ======================================================================
// Investing
// ======================================================================
export const buyInvestment = (payload) => api.post("/investments/buy/", payload);
export const getInvestments = () => api.get("/investments/");
export const toggleAutoReinvest = (id) => api.patch(`/investments/${id}/toggle_auto_reinvest/`);
export const getOrders = () => api.get("/orders/");

// ======================================================================
// Secondary market
// ======================================================================
export const getSecondaryListings = () => api.get("/secondary-market/listings/");
export const createSecondaryListing = (payload) => api.post("/secondary-market/listings/", payload);
export const buySecondaryListing = (payload) => api.post("/secondary-market/buy/", payload);

// ======================================================================
// Coupons & reinvestment
// ======================================================================
export const getCouponPayments = () => api.get("/coupons/");
export const getReinvestmentRules = () => api.get("/reinvestment-rules/");
export const setReinvestmentRule = (payload) => api.post("/reinvestment-rules/", payload);

// ======================================================================
// Documents & tax
// ======================================================================
export const getDocuments = () => api.get("/documents/");
export const uploadDocument = (formData) =>
  api.post("/documents/", formData, { headers: { "Content-Type": "multipart/form-data" } });
export const getTaxStatements = () => api.get("/tax-statements/");
export const generateTaxStatement = (taxYear) => api.post("/tax-statements/generate/", { tax_year: taxYear });

// ======================================================================
// Dashboard & tools
// ======================================================================
export const getDashboardSummary = () => api.get("/dashboard/summary/");
export const calculateInvestment = (payload) => api.post("/calculator/estimate/", payload);

// ======================================================================
// Advisor
// ======================================================================
export const getAdvisorInvestors = () => api.get("/advisor/dashboard/");

// ======================================================================
// Operations
// ======================================================================
export const getOpsKYCQueue = () => api.get("/ops/kyc-queue/");
export const runCouponBatch = () => api.post("/ops/run-coupon-batch/");
export const runReinvestmentBatch = () => api.post("/ops/run-reinvestment-batch/");

// ======================================================================
// Compliance & notifications
// ======================================================================
export const getComplianceFlags = () => api.get("/compliance-flags/");
export const resolveComplianceFlag = (id) => api.post(`/compliance-flags/${id}/resolve/`);
export const getNotifications = () => api.get("/notifications/");
export const markNotificationRead = (id) => api.patch(`/notifications/${id}/mark_read/`);

// ======================================================================
// Admin
// ======================================================================
export const getAuditLogs = (params) => api.get("/audit-logs/", { params });

export default api;