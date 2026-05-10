# Branch Protection Configuration

## Settings for main branch

Go to: https://github.com/bigknoxy/team-ai-warehouse/settings/branches

### Required Settings

1. **Branch protection rule**: `main`
2. **Require pull request reviews before merging**: ✅
   - Required approving reviews: 1
   - Dismiss stale reviews: ✅
   - Require admin bypass: ❌ (admin cannot bypass - they must also get approval)
   - Include admin: ❌

3. **Require status checks to pass before merging**: ✅
   - After CI workflow is merged, add:
     - `Warehouse CI / validate-skills`
     - `Warehouse CI / test-python`
     - `Warehouse CI / lint`

4. **Require conversation resolution**: ☐ (optional)

5. **Include administrators**: ☐ (unchecked - admins must follow rules too)

6. **Restrict who can push**: ☐ (optional - can add team restrictions)

## Quick Apply Script

Run locally with gh CLI:
```bash
# Create branch protection via API
gh api repos/bigknoxy/team-ai-warehouse/branches/main/protection \
  --method PUT \
  -f required_status_checks="null" \
  -f required_pull_request_reviews='{"dismiss_stale_reviews":true,"required_approving_review_count":1,"include_admin_by_default":false}' \
  -f restrictions="null" \
  -f enforce_admins="false"
```

Note: You need admin permissions on the repository to apply branch protection.