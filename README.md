# BondVault — Government Bonds & Fixed Income Investment Platform

An enterprise-grade digital platform for investing in Government Bonds, Treasury Bills, and other fixed income instruments — inspired by **TreasuryDirect (USA)** and **M-Akiba (Kenya)**. Built for scale, security, and regulatory compliance.

---

## 1. Overview

BondVault lets retail and institutional investors register, complete KYC, link bank accounts / mobile money, browse and invest in government securities, track portfolio performance, receive and reinvest coupon payments, trade bonds on a secondary market, and download tax statements — all through a banking-grade web experience.

**Roles:** Investor · Investment Advisor · Operations Team · Super Administrator

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript, Vite, Axios, Chart.js/Recharts |
| Backend | Django 5 + Django REST Framework |
| Database | PostgreSQL 16 |
| Cache / Broker | Redis |
| Background Jobs | Celery + Celery Beat |
| Auth | JWT (SimpleJWT), RBAC |
| Infra | Docker, Docker Compose, Nginx |
| Docs | drf-spectacular (OpenAPI/Swagger) |
| Testing | Pytest, Pytest-Django, Jest, React Testing Library |

**Architecture note:** Per current scope, the backend intentionally uses a **single Django app (`core`)** with one `models.py`, `serializers.py`, `views.py`, and `urls.py`, wired into one project-level `urls.py` / `settings.py`. This is a deliberate monolith-first approach — models are grouped by domain using clear class ordering and comments, so the app can later be split into microservices (`accounts`, `bonds`, `wallet`, `payments`, `compliance`, etc.) without changing the API contract. The frontend similarly starts lean: only `Navbar.jsx` and `Footer.jsx` as shared components, with all screens living in `pages/`.

---

## 3. Core Modules

- Authentication & KYC
- Investor Dashboard
- Bond Marketplace
- Treasury Bills Marketplace
- Portfolio Management
- Coupon & Interest Payment Engine
- Reinvestment Module
- Wallet & Cash Management
- Bank & Mobile Money Integration
- Notifications (SMS, Email, Push)
- Document Vault
- Tax Reports
- Analytics Dashboard
- Admin Panel
- Audit Logs
- Compliance & AML Monitoring
- Risk Profiling
- Investment Calculator
- Secondary Bond Trading
- Bond Auctions
- Bank/Broker API (partner integration)

---

## 4. Roles & Permissions (RBAC)

| Role | Key Permissions |
|---|---|
| **Investor** | Register, KYC, link accounts, browse & invest, view portfolio, reinvest, sell on secondary market, download statements |
| **Investment Advisor** | View assigned investors, recommend products, run calculators, view performance, no fund movement rights |
| **Operations Team** | Approve KYC, process settlements, run coupon batches, manage auctions, reconcile wallets |
| **Super Administrator** | Full system access, user/role management, audit log access, compliance overrides, system configuration |

Enforced via DRF `permission_classes` + custom `IsInvestor`, `IsAdvisor`, `IsOps`, `IsSuperAdmin` permission classes, backed by a `Role` field on the `User` model and Django Groups for fine-grained object-level permissions.

---

## 5. Investor Dashboard Widgets

- Total Portfolio Value
- Total Interest Earned
- Upcoming Coupon Payments
- Asset Allocation (pie/donut)
- Investment Growth Chart (line, time-series)
- Recent Transactions
- Active Bonds
- Maturing Investments
- Monthly Income Projection

---

## 6. Complete Project Structure

```
bondvault/
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── .env.example
│   │
│   ├── config/                        # Django project (main settings/urls)
│   │   ├── __init__.py
│   │   ├── settings.py                # env-based settings, installed apps, DRF, JWT, Celery, CORS
│   │   ├── urls.py                    # main url router -> includes api.urls
│   │   ├── celery.py                  # Celery app instance + beat schedule
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   ├── api/                           # single core app (monolith-first)
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                  # all domain models (see §7)
│   │   ├── serializers.py             # all DRF serializers
│   │   ├── views.py                   # all ViewSets / APIViews
│   │   ├── urls.py                    # app-level url router (DRF router)
│   │   ├── permissions.py             # IsInvestor, IsAdvisor, IsOps, IsSuperAdmin
│   │   ├── tasks.py                   # Celery tasks (coupons, reinvestment, notifications)
│   │   ├── signals.py                 # audit log hooks, wallet updates
│   │   ├── validators.py              # KYC, AML, financial validators
│   │   ├── utils.py                   # bond math, yield calc, accrued interest
│   │   ├── admin.py                   # Django admin registrations
│   │   ├── filters.py                 # django-filter classes for marketplace search
│   │   ├── pagination.py
│   │   ├── throttles.py
│   │   ├── migrations/
│   │   └── tests/
│   │       ├── test_auth.py
│   │       ├── test_kyc.py
│   │       ├── test_bonds.py
│   │       ├── test_portfolio.py
│   │       ├── test_coupons.py
│   │       ├── test_wallet.py
│   │       ├── test_secondary_market.py
│   │       └── test_permissions.py
│   │
│   ├── docs/
│   │   └── openapi-schema.yml         # generated via drf-spectacular
│   │
│   └── docker/
│       ├── Dockerfile
│       └── entrypoint.sh
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── .env.example
│   │
│   ├── src/
│   │   ├── main.jsx                   # React root entry, wraps <App/> with providers
│   │   ├── App.jsx                    # router + layout shell (Navbar/Footer/routes)
│   │   │
│   │   ├── services/
│   │   │   └── api.js                 # axios instance + all endpoint functions (see §8)
│   │   │
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   └── Footer.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── auth/
│   │   │   │   ├── Login.jsx
│   │   │   │   ├── Register.jsx
│   │   │   │   ├── KYCUpload.jsx
│   │   │   │   └── ForgotPassword.jsx
│   │   │   ├── dashboard/
│   │   │   │   └── InvestorDashboard.jsx
│   │   │   ├── marketplace/
│   │   │   │   ├── BondMarketplace.jsx
│   │   │   │   ├── TreasuryBillsMarketplace.jsx
│   │   │   │   ├── BondDetails.jsx
│   │   │   │   └── BondAuctions.jsx
│   │   │   ├── portfolio/
│   │   │   │   ├── Portfolio.jsx
│   │   │   │   ├── ActiveBonds.jsx
│   │   │   │   └── MaturingInvestments.jsx
│   │   │   ├── wallet/
│   │   │   │   ├── Wallet.jsx
│   │   │   │   ├── LinkBankAccount.jsx
│   │   │   │   └── LinkMobileMoney.jsx
│   │   │   ├── trading/
│   │   │   │   └── SecondaryMarket.jsx
│   │   │   ├── reinvestment/
│   │   │   │   └── ReinvestmentSettings.jsx
│   │   │   ├── documents/
│   │   │   │   ├── DocumentVault.jsx
│   │   │   │   └── TaxStatements.jsx
│   │   │   ├── tools/
│   │   │   │   ├── InvestmentCalculator.jsx
│   │   │   │   └── RiskProfileQuiz.jsx
│   │   │   ├── advisor/
│   │   │   │   └── AdvisorDashboard.jsx
│   │   │   ├── ops/
│   │   │   │   ├── OpsDashboard.jsx
│   │   │   │   ├── KYCApprovalQueue.jsx
│   │   │   │   └── CouponBatchRun.jsx
│   │   │   ├── admin/
│   │   │   │   ├── AdminPanel.jsx
│   │   │   │   ├── UserManagement.jsx
│   │   │   │   ├── AuditLogs.jsx
│   │   │   │   └── ComplianceMonitor.jsx
│   │   │   └── NotFound.jsx
│   │   │
│   │   ├── context/
│   │   │   └── AuthContext.jsx        # JWT session + role-based route guarding
│   │   │
│   │   ├── styles/
│   │   │   └── main.css               # design tokens, layout, banking-grade theme
│   │   │
│   │   └── assets/
│   │       └── logo.svg
│   │
│   └── docker/
│       ├── Dockerfile
│       └── nginx.conf
│
├── nginx/
│   └── default.conf                   # reverse proxy: /api -> backend, / -> frontend build
│
├── docker-compose.yml                 # postgres, redis, backend, celery, celery-beat, frontend, nginx
├── docker-compose.prod.yml
├── .env.example
└── README.md
```

---

## 7. Data Model Summary (`api/models.py`)

Grouped logically within the single models file:

- **Identity & KYC:** `User`, `InvestorProfile`, `KYCDocument`, `RiskProfile`
- **Accounts & Money:** `BankAccount`, `MobileMoneyAccount`, `Wallet`, `WalletTransaction`
- **Instruments:** `Bond`, `TreasuryBill`, `BondAuction`, `CouponSchedule`
- **Investing:** `Investment`, `Order`, `SecondaryMarketListing`, `Trade`
- **Income:** `CouponPayment`, `ReinvestmentRule`, `InterestAccrual`
- **Documents:** `Document`, `TaxStatement`
- **Governance:** `AuditLog`, `ComplianceFlag`, `Notification`

---

## 8. API Endpoints (`services/api.js` — general endpoint map)

```
/api/auth/register/          /api/auth/login/            /api/auth/refresh/
/api/kyc/upload/             /api/kyc/status/
/api/accounts/bank/          /api/accounts/mobile-money/
/api/bonds/                  /api/bonds/{id}/
/api/tbills/                 /api/auctions/
/api/investments/            /api/investments/{id}/sell/
/api/portfolio/summary/      /api/portfolio/growth/
/api/wallet/                 /api/wallet/deposit/         /api/wallet/withdraw/
/api/coupons/upcoming/       /api/coupons/history/
/api/reinvestment/rules/
/api/secondary-market/listings/   /api/secondary-market/trade/
/api/documents/              /api/tax/statements/
/api/calculator/estimate/
/api/notifications/
/api/admin/users/            /api/admin/audit-logs/       /api/admin/compliance/
```

Full interactive documentation is auto-generated via `drf-spectacular` at `/api/docs/`.

---

## 9. Background Jobs (Celery)

| Task | Schedule |
|---|---|
| `process_coupon_payments` | Daily |
| `run_auto_reinvestment` | Daily, after coupon run |
| `check_maturing_investments` | Daily |
| `send_notifications` (SMS/Email/Push) | Real-time queue |
| `run_aml_screening` | On transaction + nightly batch |
| `generate_tax_statements` | Annual / on-demand |
| `sync_bond_auction_results` | On auction close |

---

## 10. Getting Started

```bash
git clone <repo-url> bondvault
cd bondvault
cp .env.example .env
docker-compose up --build
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/api/`
- API Docs (Swagger): `http://localhost:8000/api/docs/`
- Admin Panel: `http://localhost:8000/admin/`

Run tests:
```bash
docker-compose exec backend pytest
cd frontend && npm test
```

---

## 11. Security & Compliance

- JWT auth with refresh rotation & token blacklisting
- Role-based access control on every endpoint
- Full audit trail (`AuditLog`) on all financial and KYC actions
- AML/CFT transaction monitoring with configurable rule thresholds
- Encrypted document storage for KYC files
- Rate limiting / throttling on auth and trading endpoints

---

## 12. Roadmap — Future Enhancements

- Money Market Funds, Corporate Bonds, Stocks & ETFs, Mutual Funds
- Retirement Planning & SIP / Recurring Investments
- Financial goal tracking (education, home, retirement)
- AI-powered investment recommendations
- Tax optimization engine
- Multi-currency & cross-border investing
- Microservice decomposition of the `api` app (`accounts`, `bonds`, `wallet`, `payments`, `compliance` as independent services behind an API gateway)

---

## 13. License

Proprietary — All rights reserved (update as needed).