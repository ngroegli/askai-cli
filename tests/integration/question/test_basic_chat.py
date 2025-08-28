"""
Semi-automated integration tests for the chat functionality.
"""
from tests.integration.test_base import SemiAutomatedTest
from tests.integration.test_utils import run_cli_command


class TestBasicChat(SemiAutomatedTest):
    """Semi-automated test for basic chat interaction with the CLI."""
    
    def run(self):
        """Run the test cases."""
        self._test_basic_chat()
        return self.results
        
    def _test_basic_chat(self):
        """Test a basic chat interaction."""
        # We'll use a simple question to test the chat functionality
        # This test requires manual verification because:
        # 1. It might need API keys to be set up
        # 2. We need to verify the actual content of the response
        test_name = "basic_chat_interaction"
        
        print("\n" + "=" * 70)
        print("Testing basic chat functionality")
        print("=" * 70)
        
        # Prompt the user to check if prerequisites are met
        ready = self.prompt_user(
            "This test will send a simple query to the AI service.\n"
            "Make sure you have valid API keys configured.\n"
            "Are you ready to proceed?",
            ["y", "n"]
        )
        
        if ready.lower() != "y":
            result = self.add_manual_result(test_name)
            result.set_failed("User cancelled the test")
            return
        
        # Simple test query (non-controversial, general knowledge)
        query = "What's the capital of France?"
        
        print(f"\nSending query: '{query}'")
        print("Please wait for the response...\n")
        
        # Run the command
        stdout, stderr, return_code = run_cli_command(["-q", query])
        
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
        print("1. The command executed successfully")
        print("2. The response contains relevant information about Paris")
        
        # Record the test result based on user input
        self.add_manual_result(test_name)
