# GitHub Actions Workflows

This project uses GitHub Actions for continuous integration, security scanning, and automated releases.

## Workflows Overview

### 1. CI Pipeline (`ci.yml`)
- **Triggers**: Push to main/develop, pull requests
- **Purpose**: Run unit tests and integration tests
- **Python Versions**: 3.12
- **Key Steps**:
  - Checkout code
  - Set up Python environment
  - Install dependencies
  - Run pytest for unit and integration tests

### 2. Code Quality (`pylint.yml`)
- **Triggers**: Push to main/develop, pull requests
- **Purpose**: Code quality analysis and linting
- **Key Steps**:
  - Run pylint on source code
  - Generate code quality reports
  - Enforce coding standards

### 3. Security Scanning (`security.yml`)
- **Triggers**:
  - Weekly schedule (Mondays at 2 AM UTC)
  - Push to main/develop branches
  - Pull requests to main/develop
  - Manual trigger
- **Purpose**: Comprehensive security analysis
- **Key Components**:
  - **Dependency Scanning**: Safety tool for known vulnerabilities
  - **Code Security Analysis**: Bandit for Python security issues
  - **Secret Detection**: Gitleaks for credential scanning
  - **Container Scanning**: Trivy for Docker image vulnerabilities
  - **SAST**: GitHub CodeQL for comprehensive static analysis
- **Reports**: All scan results uploaded as artifacts
- **Failure Conditions**: Fails on critical security issues

### 4. Release Automation (`release.yml`)
- **Triggers**:
  - Git tags matching `v*` pattern (e.g., v1.0.0)
  - Manual trigger with version input
- **Purpose**: Automated release process
- **Key Steps**:
  1. **Validation**: Version consistency check and test execution
  2. **Build**: Python package and Docker image creation
  3. **Security**: Release artifact scanning
  4. **Release**: GitHub release creation with artifacts
  5. **Post-Release**: Version bump for next development cycle

## Workflow Dependencies

```
┌─────────────┐    ┌──────────────┐
│ ci.yml      │    │ pylint.yml   │
│ (Tests)     │    │ (Quality)    │
└─────────────┘    └──────────────┘
        │                   │
        └───────┬───────────┘
                │
        ┌───────▼───────┐
        │ security.yml  │
        │ (Security)    │
        └───────────────┘
                │
        ┌───────▼───────┐
        │ release.yml   │
        │ (Deployment)  │
        └───────────────┘
```

## Required Secrets

### For Security Scanning
- **No secrets required**: All security scanning tools use free, built-in GitHub solutions

### For Release Process
- `GITHUB_TOKEN`: Automatically provided by GitHub
  - Used for GitHub Container Registry access
  - Required for creating releases and uploading artifacts

## Usage Examples

### Triggering a Release
```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

### Manual Security Scan
1. Go to Actions tab in GitHub repository
2. Select "Security Scanning" workflow
3. Click "Run workflow"
4. Specify branch and click "Run workflow"

### Manual Release
1. Go to Actions tab in GitHub repository
2. Select "Release" workflow
3. Click "Run workflow"
4. Enter version (e.g., v1.0.1) and click "Run workflow"

## Artifact Storage

- **Security Reports**: 30-day retention
  - Safety vulnerability reports (JSON)
  - Bandit security analysis (JSON)
  - Trivy container scan results (SARIF)
  - CodeQL results (available in GitHub Security tab)
- **Build Artifacts**: 7-day retention
  - Python wheel and sdist packages
  - Docker images pushed to GitHub Container Registry

## Workflow Outputs

### Security Summary
- Vulnerability counts by severity
- Security scan status overview
- Downloadable detailed reports

### Release Summary
- Release validation results
- Build and test status
- Security scan results
- Release artifact links
- Automatic version bumping status

## Best Practices

1. **Version Management**: Use semantic versioning (MAJOR.MINOR.PATCH)
2. **Pre-releases**: Use suffixes like `alpha`, `beta`, `rc` for pre-release versions
3. **Security**: Address security findings before merging
4. **Testing**: Ensure all tests pass before releasing
5. **Documentation**: Update CHANGELOG.md for major releases

## Troubleshooting

### Common Issues

1. **Release Workflow Fails**
   - Check version consistency across project files
   - Ensure all tests pass
   - Verify no critical security vulnerabilities

2. **Security Scan Failures**
   - Review security reports in workflow artifacts
   - Update vulnerable dependencies
   - Fix high-severity code security issues

3. **Docker Build Issues**
   - Check Dockerfile syntax
   - Verify .dockerignore excludes unnecessary files
   - Ensure all required files are included in build context

### Debug Steps

1. Check workflow logs in GitHub Actions
2. Download and review artifact reports
3. Run security tools locally for debugging
4. Use manual workflow triggers for testing