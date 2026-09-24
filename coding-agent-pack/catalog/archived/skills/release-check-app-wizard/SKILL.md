---
name: release-check
description: Single release validation skill (lint, test/build, cloud semantic-release run).
argument-hint: "Run release checks before publishing"
user-invokable: true
---

# Release Check

Run one pre-release flow that validates app quality locally and release behavior in Azure DevOps.

## Commands (repo root)
1. Install clean dependencies:
   `npm ci`
2. Type/lint check:
   `npm run lint`
3. Run Vitest test suite:
   `npm test`
4. Build production bundle:
   `npm run build`
5. Validate semantic-release in cloud (manual run):
   Queue `pipelines/Onboarding_Wizard_Semantic_Release.yml` in Azure DevOps

## Pass criteria
- Local commands exit with code `0`.
- Azure pipeline step `Run Semantic Release` succeeds.

## If it fails
- Report which command failed and include the error output.
- Do not release until checks pass.

## Output format
After running all checks, respond with a checklist using ✅ for pass and ❌ for fail. Keep the total response under 200 words.

**All passing example:**
✅ Install clean dependencies
✅ Type/lint check
✅ Vitest test suite
✅ Build production bundle
✅ Cloud semantic-release pipeline run

**On failure, stop the list at the failed step and show only the relevant error:**
✅ Install clean dependencies
✅ Type/lint check
❌ Build production bundle
```
<error message here>
```
Do not release until all checks pass.