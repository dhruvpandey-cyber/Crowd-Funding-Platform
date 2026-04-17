# ERD Overview

## Core Entities

1. User
- id, username, email, role, is_creator_verified

2. Category
- id, name, description

3. Campaign
- id, creator_id, category_id, title, story, goal_amount, deadline, status

4. CampaignMedia
- id, campaign_id, media_type, file, external_url

5. RewardTier
- id, campaign_id, title, amount, quantity

6. Pledge
- id, backer_id, campaign_id, reward_tier_id, amount, status

7. Payment
- id, pledge_id, transaction_id, amount, status

8. Refund
- id, payment_id, amount, reason, status

9. PayoutRequest
- id, creator_id, campaign_id, requested_amount, status

10. Notification
- id, user_id, title, message, is_read

11. Report
- id, reporter_id, campaign_id, reason, details, status

12. AuditLog
- id, actor_id, action, target_model, target_id, metadata

## Relationship Summary

1. User 1:N Campaign
2. Category 1:N Campaign
3. Campaign 1:N RewardTier
4. Campaign 1:N CampaignMedia
5. Campaign 1:N Pledge
6. User 1:N Pledge (as backer)
7. Pledge 1:1 Payment
8. Payment 1:N Refund
9. Campaign 1:N Report
10. User 1:N Notification
