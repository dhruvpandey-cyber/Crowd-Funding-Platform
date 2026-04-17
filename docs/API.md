# API Reference (Major Routes)

Base URL: /api/

## Auth

1. POST auth/register/
2. POST auth/token/
3. POST auth/token/refresh/
4. GET/PATCH auth/profile/

## Campaigns

1. GET/POST campaigns/
2. GET/PATCH/DELETE campaigns/{id}/
3. GET campaigns/mine/
4. POST campaigns/{id}/set_status/
5. POST campaigns/{id}/favorite/
6. POST campaigns/{id}/unfavorite/

## Campaign Sub-Resources

1. GET/POST campaigns/reward-tiers/
2. GET/POST campaigns/updates/
3. GET/POST campaigns/comments/
4. GET/POST campaigns/media/

## Pledges and Payments

1. GET/POST pledges/
2. GET payments/transactions/
3. GET payments/refunds/
4. GET/POST payments/payout-requests/
5. POST payments/sandbox/checkout/
6. POST payments/sandbox/refund/

## Notifications

1. GET/POST notifications/
2. POST notifications/{id}/mark_read/

## Moderation

1. GET/POST moderation/reports/
2. PATCH moderation/reports/{id}/ (admin only)
3. GET moderation/audit-logs/ (admin only)
