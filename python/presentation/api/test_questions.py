#!/usr/bin/env python3
"""
Test script specifically for the questions endpoint.
"""
import os
import sys
import json

# Add project paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "python"))

def test_questions_endpoint():
    """Test the questions endpoint functionality."""
    try:
        from presentation.api.app import create_app

        app = create_app({'TESTING': True})

        with app.test_client() as client:
            # Test question validation
            print("Testing question validation...")
            response = client.post('/api/v1/questions/validate',
                                 json={'question': 'What is AI?'})
            print(f"Validation endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"  Valid: {data.get('valid')}")
                print(f"  Errors: {data.get('errors', [])}")

            # Test invalid question validation
            print("\nTesting invalid question validation...")
            response = client.post('/api/v1/questions/validate',
                                 json={'question': ''})
            print(f"Invalid validation endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"  Valid: {data.get('valid')}")
                print(f"  Errors: {data.get('errors', [])}")

            # Test question asking (this will likely fail due to config, but let's see)
            print("\nTesting question asking endpoint...")
            response = client.post('/api/v1/questions/ask',
                                 json={'question': 'What is 2+2?', 'response_format': 'rawtext'})
            print(f"Ask endpoint: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.get_json()
                    print(f"  Response data: {json.dumps(data, indent=2)}")
                    content = data.get('content', 'MISSING')
                    print(f"  Content: '{content}'")
                    print(f"  Content length: {len(content) if content else 0}")
                    if content and len(content) > 0:
                        print("  ✓ AI response received successfully!")
                    else:
                        print("  ❌ AI response is missing or empty!")
                except Exception as e:
                    print(f"  Error parsing response: {e}")
                    print(f"  Raw response: {response.data.decode()}")
            else:
                try:
                    error_data = response.get_json()
                    print(f"  Error: {error_data.get('error')}")
                    print(f"  Code: {error_data.get('code')}")
                except:
                    print(f"  Raw response: {response.data.decode()}")

        print("\n✓ Questions endpoint tests completed!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_questions_endpoint()
    sys.exit(0 if success else 1)