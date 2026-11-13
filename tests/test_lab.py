import json
import tempfile
import unittest
from pathlib import Path
from run import parse_tool_response, run_case
from security.policy import authorize


class LabTests(unittest.TestCase):
    def test_policy_is_static(self):
        self.assertEqual(authorize("save_report")[0], True)
        self.assertEqual(authorize("export_debug_data")[0], False)

    def test_parse_states_are_distinct(self):
        self.assertEqual(parse_tool_response('{"requested_tool":"none"}'), ("none", "explicit_none"))
        self.assertEqual(parse_tool_response("plain language"), (None, "parse_error"))

    def test_injection_is_denied_and_audited(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_case("injected", "a", "b", True, Path(directory) / "result.json")
            self.assertEqual(result["requested_tool"], "export_debug_data")
            self.assertFalse(result["allowed"])
            self.assertEqual(result["parse_status"], "parsed")
            self.assertFalse(result["tool_executed"])
            lines = Path(result["audit_log"]).read_text().splitlines()
            policy_rows = [json.loads(line) for line in lines if json.loads(line)["event"] == "policy_decision"]
            self.assertEqual(policy_rows[-1]["allowed"], False)

    def test_parse_failure_fails_closed(self):
        self.assertEqual(parse_tool_response("model prose, not JSON")[1], "parse_error")


if __name__ == "__main__":
    unittest.main()
