"""Best-effort Failproof AI tracing for RepoRescue's custom runtime.

The repair workflow must remain usable when the optional SDK, credentials, or
local Failproof daemon are unavailable. The SDK records telemetry; this app
does not claim that a cloud upload or policy evaluation succeeded.
"""

from contextlib import contextmanager
import os
from typing import Optional
from uuid import uuid4

try:
    import failproofai_sdk
except Exception:  # Keep the core repair feature independent of this beta SDK.
    failproofai_sdk = None


POLICY_STATUS = "NOT_EVALUATED"
FAILPROOF_ENABLED = os.getenv("REPORESCUE_ENABLE_FAILPROOF", "").strip().lower() in {
    "1", "true", "yes", "on"
}
FAILPROOF_SDK_AVAILABLE = failproofai_sdk is not None and FAILPROOF_ENABLED


class RepairTrace:
    def __init__(self, session_id: str):
        self.session_id = session_id
        # Do not create an uncollected local event spool on hosting platforms.
        # Opt in only when the operator has configured a Failproof daemon.
        self.sdk_available = failproofai_sdk is not None and FAILPROOF_ENABLED
        self._agent_context = None
        self._session_context = None

    def _disable(self):
        self.sdk_available = False

    def __enter__(self):
        if self.sdk_available:
            try:
                self._session_context = failproofai_sdk.session(session_id=self.session_id)
                self._session_context.__enter__()
                self._agent_context = failproofai_sdk.agent("repo-rescue-repair")
                self._agent_context.__enter__()
                failproofai_sdk.event.agent_start(goal="Repair the bundled sample project bug")
            except Exception:
                self._disable()
                self._close_contexts(None, None, None)
        return self

    def _close_contexts(self, exc_type, exc, tb):
        for context in (self._agent_context, self._session_context):
            if context is not None:
                try:
                    context.__exit__(exc_type, exc, tb)
                except Exception:
                    self._disable()
        self._agent_context = None
        self._session_context = None

    def __exit__(self, exc_type, exc, tb):
        if self.sdk_available:
            try:
                failproofai_sdk.event.agent_end(
                    outcome="error" if exc_type else "success",
                    summary="Repair workflow failed" if exc_type else "Repair workflow completed",
                )
            except Exception:
                self._disable()
        self._close_contexts(exc_type, exc, tb)
        return False

    def tool(self, name: str, action, *, input_data=None):
        """Run the operation even if best-effort telemetry fails."""
        if not self.sdk_available:
            return action()

        call_id = str(uuid4())
        try:
            failproofai_sdk.event.tool_use(
                tool_name=name,
                tool_call_id=call_id,
                input=input_data,
            )
        except Exception:
            self._disable()
            return action()

        try:
            result = action()
        except Exception as error:
            try:
                failproofai_sdk.event.tool_result(
                    tool_name=name,
                    tool_call_id=call_id,
                    error=str(error),
                )
            except Exception:
                self._disable()
            raise

        try:
            failproofai_sdk.event.tool_result(
                tool_name=name,
                tool_call_id=call_id,
                output={"status": result.get("status", "ok")} if isinstance(result, dict) else None,
            )
        except Exception:
            self._disable()
        return result


@contextmanager
def repair_trace(session_id: Optional[str] = None):
    """Open a best-effort SDK session, falling back to an untraced run."""
    trace = RepairTrace(session_id or str(uuid4()))
    with trace:
        yield trace
