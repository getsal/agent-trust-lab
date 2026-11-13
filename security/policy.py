"""Authorization is explicit and independent from any model response."""
ALLOWED_TOOLS = {"save_report"}
KNOWN_TOOLS = ALLOWED_TOOLS | {"export_debug_data", "none"}


def authorize(tool_name: str) -> tuple[bool, str]:
    if tool_name in ALLOWED_TOOLS:
        return True, "tool is on the static allowlist"
    return False, "tool is not on the static allowlist"


def execute_simulated(tool_name: str, authorized: bool) -> tuple[bool, str]:
    """Never performs export; reports the simulated execution decision only."""
    if not authorized:
        return False, "not_executed: policy denied or request was unparseable"
    if tool_name == "save_report":
        return True, "simulated_save_report_completed"
    return False, "not_executed: no simulated implementation"
