#!/bin/bash

# Setup Branch Script for askai-cli
# This script helps to set up the develop branch in your repository

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up branch structure for askai-cli...${NC}"

# Check if we're in the repository root
if [ ! -f "askai.sh" ] || [ ! -d "python" ]; then
    echo -e "${YELLOW}Please run this script from the root of the askai-cli repository.${NC}"
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${YELLOW}Current branch: ${CURRENT_BRANCH}${NC}"

# Create develop branch if it doesn't exist
if ! git show-ref --verify --quiet refs/heads/develop; then
    echo -e "${YELLOW}Creating develop branch from ${CURRENT_BRANCH}...${NC}"
    git checkout -b develop
    echo -e "${GREEN}Develop branch created.${NC}"
else
    echo -e "${YELLOW}Develop branch already exists. Checking it out...${NC}"
    git checkout develop
    echo -e "${GREEN}Now on develop branch.${NC}"
fi

# Push develop branch to remote
echo -e "${YELLOW}Would you like to push the develop branch to the remote repository? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${YELLOW}Pushing develop branch to remote...${NC}"
    git push -u origin develop
    echo -e "${GREEN}Develop branch pushed to remote.${NC}"
fi

echo -e "${GREEN}Branch setup complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Create feature branches from 'develop' using: git checkout -b feature/your-feature-name"
echo -e "2. Make your changes and push to your feature branch"
echo -e "3. Create a pull request from your feature branch to 'develop'"
echo -e "4. After testing on 'develop', create a PR from 'develop' to 'main'"
