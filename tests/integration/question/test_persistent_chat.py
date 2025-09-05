"""
Tests for persistent chat functionality.
"""
import os
import re
from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import run_cli_command, verify_output_contains


class TestPersistentChat(AutomatedTest):
    """Test the persistent chat functionality.

    SAFETY MEASURES FOR PRODUCTION ISOLATION:
    1. Requires ASKAI_TESTING environment variable to be set
    2. Always uses input "0" to create NEW chats (never selects existing ones)
    3. Uses "q" to quit selection menus to avoid accidental selection
    4. Tracks created chat IDs to ensure test isolation
    """

    def __init__(self):
        super().__init__()
        self.test_chat_id = None  # Will store chat ID for follow-up tests

    def run(self):
        """Run the test cases."""
        # Safety check: Ensure we're in test environment to avoid affecting production chats
        if not os.environ.get('ASKAI_TESTING'):
            raise RuntimeError("ASKAI_TESTING environment variable not set - refusing to run tests that could affect production chats")

        # Test listing available chats
        self._test_list_chats()

        # Test creating a new persistent chat with query
        self._test_new_persistent_chat_with_query()

        # Test creating a new persistent chat with PDF
        self._test_new_persistent_chat_with_pdf()

        # Test error handling - missing query parameter
        self._test_missing_query_parameter()

        # Test error handling - non-existent PDF file
        self._test_nonexistent_pdf_file()

        # Test follow-up question in existing chat
        self._test_follow_up_question()

        # Test viewing chat history
        self._test_view_chat_history()

        # Test managing chats
        self._test_manage_chats()

        return self.results

    def _test_list_chats(self):
        """Test listing available chats."""
        stdout, stderr, return_code = run_cli_command(["-lc"])

        # Test outcome is handled automatically
        # The command should be recognized whether or not chats exist
        expected_patterns = [
            r"chat|chats|available|list|found|No.*chats",  # Should see reference to chats
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)

        self.add_result(
            "list_chats",
            success,
            "Chat list command recognized" if success
            else f"Chat list command not recognized: {missing}",
            {
                "command": "askai.py -lc",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_new_persistent_chat_with_query(self):
        """Test creating a new persistent chat with query."""
        test_name = "new_persistent_chat_query"

        # Simple test query with persistent chat flag
        query = "Tell me a short fun fact about space"

        # Run the command with persistent chat flag and query flag
        # Use stdin "0" to explicitly select "Create new chat" option (NOT existing chats)
        stdout, stderr, return_code = run_cli_command(["-pc", "-q", query], input_text="0\n")

        # Verify we created a NEW chat (not selected an existing one)
        new_chat_indicators = [
            r"Create.*new.*chat|Creating.*chat|New.*chat.*created",
        ]
        new_chat_created, _ = verify_output_contains(stdout, new_chat_indicators)

        # Try to extract chat ID from output
        chat_id_match = re.search(r'Chat ID:\s*([A-Za-z0-9\-]+)', stdout)
        if chat_id_match:
            self.test_chat_id = chat_id_match.group(1)

        # Check for successful chat creation patterns
        success_patterns = [
            r"Chat ID|chat.*created|response|fact|space",
        ]

        success, missing = verify_output_contains(stdout, success_patterns)
        no_errors = return_code == 0

        test_success = success and no_errors

        self.add_result(
            test_name,
            test_success,
            "Persistent chat with query created successfully" if test_success
            else f"Persistent chat creation failed - {missing if not success else 'Command returned error'}",
            {
                "command": f"askai.py -pc -q '{query}' (with input '0' to create NEW chat)",
                "chat_id": self.test_chat_id if self.test_chat_id else "Not detected",
                "new_chat_created": new_chat_created,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_new_persistent_chat_with_pdf(self):
        """Test creating a new persistent chat with PDF."""
        test_name = "new_persistent_chat_pdf"

        # Check if test PDF exists
        test_pdf = "/home/nicola/Git/askai-cli/tests/test_resources/test.pdf"
        if not os.path.exists(test_pdf):
            # Try alternative location
            test_pdf = "tests/test_resources/sample.pdf"
            if not os.path.exists(test_pdf):
                self.add_result(
                    test_name,
                    False,
                    "Test PDF file not found",
                    {"expected_path": test_pdf}
                )
                return

        # Run the command with persistent chat flag and PDF
        # Use stdin "0" to explicitly select "Create new chat" option (NOT existing chats)
        stdout, stderr, return_code = run_cli_command(["-pc", "--pdf", test_pdf], input_text="0\n")

        # Verify we created a NEW chat (not selected an existing one)
        new_chat_indicators = [
            r"Create.*new.*chat|Creating.*chat|New.*chat.*created",
        ]
        new_chat_created, _ = verify_output_contains(stdout, new_chat_indicators)

        # Check for successful PDF analysis patterns
        success_patterns = [
            r"Chat ID|chat.*created|analyzed|content|PDF|document|text",
        ]

        success, missing = verify_output_contains(stdout, success_patterns)
        no_errors = return_code == 0

        test_success = success and no_errors

        self.add_result(
            test_name,
            test_success,
            "Persistent chat with PDF created successfully" if test_success
            else f"Persistent chat with PDF failed - {missing if not success else 'Command returned error'}",
            {
                "command": f"askai.py -pc --pdf {test_pdf} (with input '0' to create NEW chat)",
                "new_chat_created": new_chat_created,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_missing_query_parameter(self):
        """Test error handling when query parameter is missing."""
        # Run command with persistent chat but no query or content
        # Use "q" to quit the chat selection to avoid affecting existing chats
        stdout, stderr, return_code = run_cli_command(["-pc"], input_text="q\n")

        # Check if proper error handling occurs or interactive prompt appears
        error_patterns = [
            r"error|Error|ERROR|missing|required|invalid|usage|help",
        ]

        # For this test, we expect either an error message or interactive prompt
        success, missing = verify_output_contains(stdout + stderr, error_patterns)

        # If no error patterns found, check if it enters interactive mode (which is also valid)
        if not success:
            interactive_patterns = [r"Enter|Type|Input|>|>>|:|Options|Select|Choose|Quit"]
            interactive_success, _ = verify_output_contains(stdout, interactive_patterns)
            success = interactive_success

        self.add_result(
            "missing_query_error",
            success,
            "Proper error handling or interactive mode detected" if success
            else f"No proper error handling detected: {missing}",
            {
                "command": "askai.py -pc (with input 'q' to quit safely)",
                "stdout": stdout[:300] + ("..." if len(stdout) > 300 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_nonexistent_pdf_file(self):
        """Test error handling with non-existent PDF file."""
        nonexistent_pdf = "/tmp/nonexistent_file_12345.pdf"

        # Run command with persistent chat and non-existent PDF
        # Use stdin "0" to automatically select "Create new chat" option, even though the PDF doesn't exist
        stdout, stderr, return_code = run_cli_command(["-pc", "--pdf", nonexistent_pdf], input_text="0\n")

        # Check if proper error handling occurs
        error_patterns = [
            r"error|Error|ERROR|not.*found|does.*not.*exist|No.*such.*file|file.*not.*found",
        ]

        success, missing = verify_output_contains(stdout + stderr, error_patterns)

        self.add_result(
            "nonexistent_pdf_error",
            success,
            "Proper error handling for non-existent PDF detected" if success
            else f"No proper error handling detected: {missing}",
            {
                "command": f"askai.py -pc --pdf {nonexistent_pdf}",
                "stdout": stdout[:300] + ("..." if len(stdout) > 300 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_follow_up_question(self):
        """Test asking a follow-up question in the same chat."""
        test_name = "follow_up_question"

        if not self.test_chat_id:
            self.add_result(
                test_name,
                False,
                "No chat ID available from previous test",
                {"note": "Previous test must create a chat first"}
            )
            return

        # Follow-up question related to the first query
        follow_up_query = "Can you tell me more details about that?"

        # Run the command with existing chat ID
        stdout, stderr, return_code = run_cli_command(["-pc", self.test_chat_id, "-q", follow_up_query])

        # Check for successful follow-up patterns
        success_patterns = [
            r"more|details|additional|further|expand|about|that|response|answer",
        ]

        success, missing = verify_output_contains(stdout, success_patterns)
        no_errors = return_code == 0

        test_success = success and no_errors

        self.add_result(
            test_name,
            test_success,
            "Follow-up question processed successfully" if test_success
            else f"Follow-up question failed - {missing if not success else 'Command returned error'}",
            {
                "command": f"askai.py -pc {self.test_chat_id} -q '{follow_up_query}'",
                "chat_id": self.test_chat_id,
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

    def _test_view_chat_history(self):
        """Test viewing chat history."""
        # Test viewing chat history without specifying ID (should list available chats)
        # Use "q" to quit if it prompts for selection to avoid affecting existing chats
        stdout, stderr, return_code = run_cli_command(["-vc"], input_text="q\n")

        # Check if command is recognized
        expected_patterns = [
            r"chat|history|available|select|choose|found|No.*chats",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)

        self.add_result(
            "view_chat_history",
            success,
            "View chat history command recognized" if success
            else f"View chat history command not recognized: {missing}",
            {
                "command": "askai.py -vc (with input 'q' to quit safely)",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )

        # If we have a test chat ID, also test viewing specific chat
        if self.test_chat_id:
            stdout2, stderr2, return_code2 = run_cli_command(["-vc", self.test_chat_id])

            # Check if specific chat history is displayed
            history_patterns = [
                r"chat|history|conversation|message|query|response",
            ]

            success2, missing2 = verify_output_contains(stdout2, history_patterns)

            self.add_result(
                "view_specific_chat_history",
                success2,
                "Specific chat history displayed" if success2
                else f"Specific chat history not displayed: {missing2}",
                {
                    "command": f"askai.py -vc {self.test_chat_id} (viewing OUR test chat only)",
                    "stdout": stdout2[:500] + ("..." if len(stdout2) > 500 else ""),
                    "stderr": stderr2 if stderr2 else "No errors",
                    "return_code": return_code2
                }
            )

    def _test_manage_chats(self):
        """Test chat management functionality."""
        # Test the manage chats command
        stdout, stderr, return_code = run_cli_command(["--manage-chats"])

        # Check if command is recognized
        expected_patterns = [
            r"manage|repair|delete|corrupted|chat.*files|available.*chats|No.*chats",
        ]

        success, missing = verify_output_contains(stdout, expected_patterns)

        self.add_result(
            "manage_chats",
            success,
            "Manage chats command recognized" if success
            else f"Manage chats command not recognized: {missing}",
            {
                "command": "askai.py --manage-chats",
                "stdout": stdout[:500] + ("..." if len(stdout) > 500 else ""),
                "stderr": stderr if stderr else "No errors",
                "return_code": return_code
            }
        )
