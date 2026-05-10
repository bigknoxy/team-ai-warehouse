#!/usr/bin/env bash
# configure-branch-protection.sh — Configure branch protection for main branch.
# Requires: gh CLI with admin permissions on the repository.
# Usage: bash scripts/configure-branch-protection.sh

REPO="${1:-bigknoxy/team-ai-warehouse}"

echo "Configuring branch protection for $REPO..."
echo "Requirements:"
echo "  - Require PR reviews"
echo "  - Require CI passing"
echo "  - Require admin bypass for bigknoxy"
echo ""

# Branch protection configuration
# This requires admin privileges on the repo
gh api "repos/$REPO/protection/branch:main" \
  --method PUT \
  --header "Accept: application/vnd.github+json" \
  -F "required_status_checks[]={context='Warehouse CI/validate-skills'}" \
  -F "required_status_checks_strict=true" \
  -F "required_reviewDismissalRestrictions[]=bigknoxy" \
  -F "dismiss_stale_reviews=true" \
  -F "require_code_owner_reviews=false" \
  -F "required_approving_review_count=1" \
  -F "include_admins=false" \
  2>/dev/null && echo "Branch protection applied!" || echo "Failed (may need admin permissions)"