# Branch Protection Guide for askai-cli

## Branch Strategy

1. `main` - stable, production-ready code
2. `develop` - integration branch for new features
3. Feature branches - created from `develop` for individual features

## Branch Protection Settings for `main`

To protect the main branch and enforce code quality via Pylint checks, go to the GitHub repository settings and set up the following:

1. Go to your repository on GitHub
2. Click on "Settings"
3. Click on "Branches" in the left sidebar
4. Under "Branch protection rules", click "Add rule"
5. Configure the following settings:

   - Branch name pattern: `main`
   - ✅ Require a pull request before merging
     - ✅ Require approvals (at least 1)
   - ✅ Require status checks to pass before merging
     - ✅ Require branches to be up to date before merging
     - Add status check: `Enforce critical errors` (this will appear after the first workflow run)
   - ✅ Include administrators (enforce rules for everyone)
   - ❌ Allow force pushes (keep this disabled)
   - ❌ Allow deletions (keep this disabled)

## Development Workflow

1. Create feature branches from `develop`
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/your-feature-name
   ```

2. Make changes and commit to your feature branch
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin feature/your-feature-name
   ```

3. Create a Pull Request from your feature branch to `develop`

4. After review and approval, merge to `develop`

5. Periodically, create a PR from `develop` to `main` when features are ready for production

## CI/CD Workflow

The GitHub Actions workflow will:
1. Run on every push to `main` and `develop`
2. Run on every pull request to `main`
3. Execute Pylint checks against Python code
4. Fail if critical errors are found
5. Report warnings but not fail the build (yet)

This ensures that code with critical issues cannot be merged into the main branch.
