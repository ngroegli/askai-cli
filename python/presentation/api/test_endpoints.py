#!/usr/bin/env python3
"""
Quick test to verify API root endpoints work properly.
"""
import os
import sys

# Add project paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "python"))

def test_app_creation():
    """Test that the Flask app can be created and root routes work."""
    try:
        from presentation.api.app import create_app

        app = create_app({'TESTING': True})

        # Test app creation
        print("✓ Flask app created successfully")

        # Test that routes are registered
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.methods} {rule.rule}")

        print(f"✓ Registered {len(routes)} routes:")
        for route in sorted(routes):
            print(f"  {route}")

        # Test root endpoints with test client
        with app.test_client() as client:
            # Test root redirect
            response = client.get('/')
            print(f"✓ Root endpoint: {response.status_code} (should be 302 redirect)")

            # Test API info
            response = client.get('/api')
            print(f"✓ API info endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"  API name: {data.get('name')}")
                print(f"  API version: {data.get('version')}")

            # Test API v1 info
            response = client.get('/api/v1')
            print(f"✓ API v1 info endpoint: {response.status_code}")

            # Test favicon
            response = client.get('/favicon.ico')
            print(f"✓ Favicon endpoint: {response.status_code} (should be 204)")

            # Test 404 handling
            response = client.get('/nonexistent')
            print(f"✓ 404 handler: {response.status_code}")
            if response.status_code == 404:
                data = response.get_json()
                print(f"  404 message: {data.get('message')}")

        print("\n🎉 All endpoint tests passed!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_creation()
    sys.exit(0 if success else 1)