#!/bin/bash

echo "Testing AskAI API with curl..."

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s http://localhost:8080/api/v1/health | jq .

echo -e "\n2. Testing questions validation..."
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?"}' \
  http://localhost:8080/api/v1/questions/validate | jq .

echo -e "\n3. Testing questions ask..."
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "What is 2+2?", "response_format": "rawtext"}' \
  http://localhost:8080/api/v1/questions/ask | jq .

echo -e "\nAPI testing completed!"