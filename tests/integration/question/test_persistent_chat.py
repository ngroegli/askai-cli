"""
Tests for persistent chat functionality.
"""
from tests.integration.test_base import SemiAutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains, TestResult


class TestPersistentChat(SemiAutomatedTest):
    """Test the persistent chat functionality."""

    def add_result(self, test_name, success, message, details=None):
        """Add a test result to the results list."""
        result = TestResult(test_name)
        if success:
            result.set_passed(message)
        else:
            result.set_failed(message)
            
        if details:
            for k, v in details.items():
                result.add_detail(k, v)
                
        self.results.append(result)
        return result

    def run(self):
        """Run the test cases."""
        # Test listing available chats
        self._test_list_chats()
        
        # Test creating a new persistent chat (semi-automated)
        self._test_new_persistent_chat()
        
        return self.results
        
    def _test_list_chats(self):
        """Test listing available chats."""
        stdout, stderr, return_code = run_cli_command(["-lc"])
        
        # Test outcome is handled automatically
        # The command should be recognized whether or not chats exist
        expected_patterns = [
            r"chat|chats",  # Should see reference to chats
        ]
        
        success, missing = verify_output_contains(stdout, expected_patterns)
        
        self.add_result(
            "list_chats",
            success,
            "Chat list command recognized" if success 
            else f"Chat list command not recognized: {missing}",
            {
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
        
    def _test_new_persistent_chat(self):
        """Test creating a new persistent chat."""
        # This requires manual verification as it involves actual AI responses
        test_name = "new_persistent_chat"
        
        print("\n" + "=" * 70)
        print("Testing creation of new persistent chat")
        print("=" * 70)
        
        # Prompt the user to check if prerequisites are met
        ready = self.prompt_user(
            "This test will create a new persistent chat.\n"
            "Make sure you have valid API keys configured.\n"
            "Are you ready to proceed?",
            ["y", "n"]
        )
        
        if ready.lower() != "y":
            result = self.add_manual_result(test_name)
            result.set_failed("User cancelled the test")
            return
        
        # Simple test query with persistent chat flag
        query = "Tell me a short fun fact"
        
        print(f"\nCreating new persistent chat with query: '{query}'")
        print("Please wait for the response...\n")
        
        # Run the command with persistent chat flag and query flag
        stdout, stderr, return_code = run_cli_command(["-pc", "-q", query])
        
        # Print the response for the user to verify
        print("\nResponse received:")
        print("-" * 70)
        print(stdout)
        print("-" * 70)
        if stderr:
            print("Errors:")
            print(stderr)
        print(f"Return code: {return_code}")
        
        # Ask the user to verify
        print("\nPlease verify:")
        print("1. A new chat was created successfully")
        print("2. You received a response to your query")
        print("3. There's an indication of the chat being persistent")
        
        # Record the test result based on user input
        self.add_manual_result(test_name)
