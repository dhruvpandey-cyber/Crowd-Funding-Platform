# Crowd-Funding Platform (Django + SQLITE)

Production-style crowdfunding platform (backend + frontend) for a college major project.

## Implemented Modules

- Accounts with role-based users (Backer, Creator, Admin)
- JWT authentication (register/login/refresh/profile)
- Campaign management (category, campaign CRUD, reward tiers)
- Campaign updates, comments, favorites
- Pledge system with core validation rules
- Payment, refund, and payout-request data models + APIs
- Notifications API with mark-as-read
- Moderation (reports + audit logs)
- Admin panel registration for all key models
- Template-based frontend with campaign discovery, detail, pledge, dashboard, moderation, and analytics pages
- Campaign media upload/display support
- Sandbox checkout/refund simulation for payment flow demos

## Tech Stack

- Django
- Django REST Framework
- SQL Database (SQLite by default, PostgreSQL-ready via env)
- JWT via `djangorestframework-simplejwt`

## API Base

- `http://127.0.0.1:8000/api/`

## Main Endpoints

- `api/health/`
- `api/auth/register/`
- `api/auth/token/`
- `api/auth/token/refresh/`
- `api/auth/profile/`
- `api/campaigns/`
- `api/campaigns/categories/`
- `api/campaigns/reward-tiers/`
- `api/campaigns/updates/`
- `api/campaigns/comments/`
- `api/campaigns/media/`
- `api/pledges/`
- `api/payments/transactions/`
- `api/payments/refunds/`
- `api/payments/payout-requests/`
- `api/payments/sandbox/checkout/`
- `api/payments/sandbox/refund/`
- `api/notifications/`
- `api/moderation/reports/`
- `api/moderation/audit-logs/`

## Setup

1. Create and activate virtual environment (already configured in this workspace).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy env template:

```bash
copy .env.example .env
```

4. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create admin user:

```bash
python manage.py createsuperuser
```

6. Start server:

```bash
python manage.py runserver
```

## Frontend Routes

- `/`
- `/auth/`
- `/campaigns/`
- `/campaigns/<id>/`
- `/create/`
- `/dashboard/`
- `/analytics/`
- `/admin-panel/`

## Seed Demo Data

Run:

```bash
python manage.py seed_demo_data
```

Creates demo users, campaigns, rewards, pledges, payments, notifications, and moderation reports.

Demo credentials:

- `admin_demo / Admin@12345`
- `creator_demo / Creator@12345`
- `backer_demo / Backer@12345`

## Project Docs

- `docs/ERD.md`
- `docs/API.md`
- `docs/FLOW.md`
- `docs/TEST_CASES.md`

## Notes For Final Submission

- Switch to PostgreSQL in `.env` for final demo/deployment.
- Add payment gateway integration (Stripe/Razorpay sandbox) for live pledge capture.
- Add frontend (React/Next.js or Django templates) for full-stack showcase.
- Add automated tests for business rules and API permissions.
