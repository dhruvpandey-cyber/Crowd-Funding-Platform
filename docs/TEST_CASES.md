# Test Cases

## Authentication

1. Register user with valid payload -> 201
2. Login with valid credentials -> access token
3. Access protected endpoint without token -> 401

## Campaigns

1. Creator can create campaign -> 201
2. Non-owner cannot update another creator campaign -> 403
3. Campaign list returns progress and raised amount

## Pledges/Payments

1. Backer can create pledge on active campaign -> 201
2. Creator cannot pledge own campaign -> 400
3. Sandbox checkout creates Payment + marks pledge CAPTURED
4. Sandbox refund creates Refund + marks pledge REFUNDED

## Moderation

1. User can create report -> 201
2. Non-admin cannot update report status -> 403
3. Admin can resolve report -> 200

## Frontend

1. / loads landing page
2. /campaigns loads list and detail links
3. /campaigns/{id}/ allows pledge form submission
4. /create uploads optional image
5. /dashboard loads profile, pledges, notifications
6. /analytics renders chart cards
