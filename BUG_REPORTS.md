# Bug Reports

This file contains manual bug reports and issues found during testing.

## Format:
- **Bug ID**: Unique identifier
- **Title**: Brief description
- **Description**: Detailed description
- **Steps to Reproduce**: Step-by-step instructions
- **Expected Result**: What should happen
- **Actual Result**: What actually happens
- **Severity**: Critical, High, Medium, Low
- **Status**: Open, In Progress, Resolved, Closed
- **Date Reported**: YYYY-MM-DD
- **Reported By**: Tester name
- **Assigned To**: Developer name
- **Resolution**: How it was fixed (if resolved)

## Open Bugs

### Bug #001
**Title**: Login form does not validate email format
**Description**: The login form accepts any string as username, but if email is used, it should validate format.
**Steps to Reproduce**:
1. Go to /auth/
2. Enter invalid email in username field
3. Try to login
**Expected Result**: Form should show validation error for invalid email
**Actual Result**: No validation error
**Severity**: Medium
**Status**: Open
**Date Reported**: 2026-04-19
**Reported By**: Automated Test
**Assigned To**: TBD

### Bug #002
**Title**: Campaign creation allows negative goal amount
**Description**: API accepts negative values for goal_amount
**Steps to Reproduce**:
1. POST to /api/campaigns/ with negative goal_amount
**Expected Result**: Validation error
**Actual Result**: Campaign created with negative goal
**Severity**: High
**Status**: Open
**Date Reported**: 2026-04-19
**Reported By**: Automated Test
**Assigned To**: TBD

## Resolved Bugs

(None yet)

## Closed Bugs

(None yet)