"""Failproof AI tracing for RepoRescue's custom runtime.

The official Python SDK records events; it does not evaluate policies for a
custom runtime. Policy enforcement must be added through a validated runtime
hook with Failproof AI support.
"""

from contextlib import contextmanager
from typing import Optional
from uuid import uuid4

try:
    import failproofai_sdk
except ImportError:  # The app remains usable before optional SDK installation.
    failproofai_sdk = None


POLICY_STATUS = "NOT_EVALUATED"
FAILPROOF_SDK_AVAILABLE = failproofai_sdk is not None


class RepairTrace:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.sdk_available = failproofai_sdk is not None
        self._agent_context = None
        self._session_context = None

    def __enter__(self):
        if self.sdk_available:
            self._session_context = failproofai_sdk.session(session_id=self.session_id)
            self._session_context.__enter__()
            self._agent_context = failproofai_sdk.agent("repo-rescue-repair")
            self._agent_context.__enter__()
            failproofai_sdk.event.agent_start(goal="Repair the bundled sample project bug")
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.sdk_available:
            failproofai_sdk.event.agent_end(
                outcome="error" if exc_type else "success",
                summary="Repair workflow failed" if exc_type else "Repair workflow completed",
            )
            self._agent_context.__exit__(exc_type, exc, tb)
            self._session_context.__exit__(exc_type, exc, tb)
        return False

    def tool(self, name: str, action, *, input_data=None):
        """Record an actual action and its result, then return the result."""
        if not self.sdk_available:
            return action()

        call_id = str(uuid4())
        failproofai_sdk.event.tool_use(
            tool_name=name,
            tool_call_id=call_id,
            input=input_data,
        )
        try:
            result = action()
        except Exception as error:
            failproofai_sdk.event.tool_result(
                tool_name=name,
                tool_call_id=call_id,
                error=str(error),
            )
            raise
        failproofai_sdk.event.tool_result(
            tool_name=name,
            tool_call_id=call_id,
            output={"status": result.get("status", "ok")} if isinstance(result, dict) else None,
        )
        return result


@contextmanager
def repair_trace(session_id: Optional[str] = None):
    """Open a real Failproof session when the SDK is installed."""
    trace = RepairTrace(session_id or str(uuid4()))
    with trace:
        yield trace
