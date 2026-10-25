
import streamlit as st
import json
from pathlib import Path
from core.orchestrator import run_repair
from core.verifier import verify
from core.failproof import FAILPROOF_SDK_AVAILABLE

PROJECT_DIR = str(
    Path(__file__).resolve().parent / "sample_project"
)

# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="RepoRescue AI | Command Center",
    page_icon="🛟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================
# SESSION STATE
# =====================================

if "repair_result" not in st.session_state:
    st.session_state.repair_result = None

if "incident_count" not in st.session_state:
    st.session_state.incident_count = 0
if "verified_repair_count" not in st.session_state:
    st.session_state.verified_repair_count = 0

# =====================================
# PREMIUM DARK THEME
# =====================================

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(
            ellipse at 85% 0%,
            rgba(79,70,229,0.16),
            transparent 40%
        ),
        #080d19;
    color: #e8edf7;
}

.block-container {
    max-width: 1320px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #0e1627;
    border-right: 1px solid #243047;
}

h1, h2, h3 {
    letter-spacing: -0.5px;
}

.hero {
    background: linear-gradient(
        115deg,
        #142340,
        #172b46,
        #143c49
    );
    border: 1px solid #28475f;
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 24px;
}

.hero h1 {
    font-size: 2.6rem;
    color: #ffffff;
    margin: 0;
}

.hero p {
    color: #b4c8db;
    margin-top: 10px;
    font-size: 1rem;
}

.tag {
    display: inline-block;
    background: #123b48;
    color: #67e8f9;
    padding: 6px 12px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 14px;
}

.agent-card {
    background: #121d31;
    border: 1px solid #283650;
    border-radius: 16px;
    padding: 22px;
    min-height: 145px;
    margin-bottom: 12px;
}

.agent-title {
    color: #f1f5f9;
    font-weight: 700;
    font-size: 18px;
}

.agent-desc {
    color: #94a3b8;
    font-size: 14px;
    margin-top: 10px;
}

.agent-status {
    color: #67e8f9;
    font-size: 12px;
    margin-top: 15px;
    font-weight: 600;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(
        90deg,
        #0891b2,
        #4f46e5
    );
    color: white;
    border: none;
    border-radius: 12px;
    min-height: 48px;
    font-weight: 700;
}

div.stButton > button[kind="primary"]:hover {
    color: white;
    border: 1px solid #67e8f9;
}

[data-testid="stMetric"] {
    background: #121d31;
    border: 1px solid #283650;
    border-radius: 14px;
    padding: 18px;
}

[data-testid="stCode"] {
    border: 1px solid #283650;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:
    st.title("🛟 RepoRescue AI")
    st.caption("SAMPLE PROJECT REPAIR WORKSPACE")

    st.divider()

    st.subheader("⚙️ Configuration")

    project = st.selectbox(
        "Target repository",
        ["Sample Calculator"]
    )

    st.divider()

    st.subheader("🔌 Integrations")
    if FAILPROOF_SDK_AVAILABLE:
        st.success("Failproof AI: optional SDK instrumentation enabled")
        st.caption("The SDK queues events locally. Cloud delivery requires a configured, running Failproof daemon and has not been verified here.")
    else:
        st.info("Failproof AI: tracing is off; repairs run without the optional integration.")
    st.success("Repair backend: Connected to the bundled sample project")

    st.divider()

    st.metric(
        "Incidents submitted",
        st.session_state.incident_count
    )

    if st.button("Clear Results", use_container_width=True):
        st.session_state.repair_result = None
        st.rerun()

    st.caption("RepoRescue AI • Hackathon MVP")

# =====================================
# HERO
# =====================================

st.markdown("""
<div class="hero">
    <div class="tag">● SAMPLE PROJECT MODE</div>
    <h1>🛟 RepoRescue AI</h1>
    <p>
        Controlled repair of the bundled sample calculator,
        with human approval and pytest verification.
    </p>
</div>
""", unsafe_allow_html=True)

# =====================================
# OVERVIEW
# =====================================

st.subheader("📊 Command Center")

m1, m2, m3, m4 = st.columns(4)

m1.metric("System Mode", "SAMPLE")
m2.metric(
    "Incidents",
    st.session_state.incident_count
)
m3.metric("AI Agents", "3 Planned")
m4.metric("Verified Repairs", st.session_state.verified_repair_count)

st.caption(
    "Repairs are limited to the bundled sample calculator project."
)

st.divider()

# =====================================
# INCIDENT FORM
# =====================================

st.subheader("🐛 New Incident")

with st.container(border=True):
    st.write(
        "Describe the issue. The investigator checks the bundled sample project for its known calculator bug."
    )

    with st.form("repair_form"):
        bug = st.text_area(
            "Bug description",
            placeholder=(
                "Example: Calculator returns 13 "
                "instead of 30 when multiplying 10 by 3."
            ),
            height=120
        )

        run = st.form_submit_button(
            "🚀 Launch Repair Workflow",
            type="primary",
            use_container_width=True
        )

# =====================================
# REPAIR PROPOSAL
# =====================================


if run:
    if not bug.strip():
        st.warning("Please enter a bug description.")
    else:
        with st.spinner("Investigating the sample project..."):
            try:
                result = run_repair(
                    PROJECT_DIR,
                    approval=False
                )

                st.session_state.repair_result = result
                st.session_state.incident_count += 1

                if result["status"] == "AWAITING_APPROVAL":
                    st.info(
                        "The backend found a known bug. "
                        "The patch has not been applied."
                    )
                else:
                    st.warning(
                        "Workflow status: "
                        + result["status"]
                    )

            except Exception as error:
                st.error("The repair workflow could not complete. Check the local application log for details.")


# =====================================
# AGENT WORKFLOW
# =====================================

st.divider()
st.subheader("🤖 Multi-Agent Repair Pipeline")

a1, a2, a3 = st.columns(3)

current = st.session_state.repair_result or {}
stage = current.get("status", "IDLE")
agent_states = {
    "🔍 Investigator": "COMPLETE" if current.get("diagnosis", {}).get("ok") else ("READY" if stage == "IDLE" else "NO MATCH"),
    "🛠️ Repairer": "PROPOSAL READY" if stage == "AWAITING_APPROVAL" else ("APPLIED" if stage in ("VERIFIED", "VERIFICATION_FAILED") else "READY"),
    "🧪 Verifier": "PASSED" if stage == "VERIFIED" else ("FAILED" if stage == "VERIFICATION_FAILED" else "WAITING FOR APPROVAL"),
}

agents = [
    (
        "🔍 Investigator",
        "Checks the bundled calculator for its known faulty expression."
    ),
    (
        "🛠️ Repairer",
        "Prepares a reviewable patch for the known sample bug."
    ),
    (
        "🧪 Verifier",
        "Runs the sample project's pytest file after approval."
    )
]

for column, agent in zip([a1, a2, a3], agents):
    name, description = agent

    with column:
        st.markdown(
            f"""
            <div class="agent-card">
                <div class="agent-title">{name}</div>
                <div class="agent-desc">{description}</div>
                <div class="agent-status">{agent_states.get(name, 'READY')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# =====================================

# =====================================
# REAL BACKEND RESULTS
# =====================================

result = st.session_state.repair_result

st.divider()
st.subheader("📋 Repair Workspace")

if result is None:
    st.info(
        "No incident submitted yet. "
        "Describe a bug and launch the workflow."
    )

else:
    status = result.get("status", "UNKNOWN")

    if status == "AWAITING_APPROVAL":
        st.warning("Patch proposed — awaiting your approval.")
    elif status == "VERIFIED":
        st.success("Patch applied and pytest verification passed.")
    elif status == "VERIFICATION_FAILED":
        st.error("Patch applied, but pytest verification failed. Review the test output.")
    elif status == "BLOCKED":
        st.error("Repair blocked.")
    else:
        st.error("Workflow status: " + status)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Diagnosis",
        "💻 Code Patch",
        "🧪 Verification",
        "🛡️ Failproof Audit"
    ])

    if status == "AWAITING_APPROVAL":
        st.warning("Review the exact change below. Approval writes only sample_project/calculator.py and then runs its pytest file.")
        approve_col, cancel_col = st.columns(2)
        with approve_col:
            approved = st.button("Approve patch and run tests", type="primary", use_container_width=True)
        with cancel_col:
            cancelled = st.button("Discard proposal", use_container_width=True)
        if approved:
            with st.spinner("Applying the approved patch and running sample project tests..."):
                try:
                    st.session_state.repair_result = run_repair(PROJECT_DIR, approval=True)
                    if st.session_state.repair_result.get("status") == "VERIFIED":
                        st.session_state.verified_repair_count += 1
                    st.rerun()
                except Exception:
                    st.error("The approved repair could not complete. Check the local application log for details.")
        if cancelled:
            st.session_state.repair_result = None
            st.rerun()

    # Diagnosis
    with tab1:
        st.subheader("Real Backend Diagnosis")

        diagnosis = result.get("diagnosis", {})

        if isinstance(diagnosis, dict):
            st.write(
                diagnosis.get(
                    "diagnosis",
                    "No diagnosis available."
                )
            )
            st.caption(
                "File: " + str(
                    diagnosis.get("file", "Unknown")
                )
            )
        else:
            st.write(diagnosis)

    # Code patch
    with tab2:
        st.subheader("Patch Review")

        patch = result.get("patch", {})

        if isinstance(patch, dict):
            st.write(
                patch.get("reason", "No reason provided.")
            )

            if patch.get("updated"):
                if patch.get("original"):
                    st.write("**Before**")
                    st.code(patch["original"], language="python")
                    st.write("**Proposed after**")
                st.code(
                    patch["updated"],
                    language="python"
                )
            else:
                st.info("No patch available.")
        else:
            st.info("No patch available.")

        st.caption("This exact change is applied only after approval.")

    # Verification
    with tab3:
        st.subheader("Test Verification")
        verification = result.get("verification")
        if verification is None:
            st.info("Tests have not run. They run only after you approve and apply the patch.")
        else:
            st.metric("Pytest", "PASSED" if verification.get("ok") else "FAILED", delta=f"Exit code {verification.get('exit_code')}")
            st.code(verification.get("output") or "Pytest completed without output.", language="text")

    # Failproof
    with tab4:
        st.subheader("Failproof AI Audit")
        fp = result.get("failproof", {})
        if fp.get("sdk_available"):
            st.write("**Failproof session / trace ID**")
            st.code(fp.get("session_id") or "Unavailable", language="text")
            st.info("The Failproof SDK instrumentation ran for this session. The SDK queues events on the app host; cloud delivery was not verified and requires a configured, running Failproof daemon.")
        else:
            st.write("**Failproof session / trace ID**")
            st.code("Unavailable", language="text")
            st.info("No Failproof trace was emitted. The repair workflow continues without the optional integration.")
        st.write("**Failproof policy outcome**")
        st.warning("NOT EVALUATED — Failproof documents tracing for custom agents, but policy enforcement requires a custom runtime hook validated with Failproof AI.")
        st.write("**Local safeguards**")
        st.caption("Human approval, sample-project path restrictions, exact known-bug matching, and stale-file checks are enforced by RepoRescue's backend. These are not Failproof policy verdicts.")

    # Download report
    st.divider()
    st.subheader("📥 Export Incident Report")

    report = json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )

    st.download_button(
        "⬇️ Download Backend Report",
        data=report,
        file_name="repo_rescue_report.json",
        mime="application/json",
        use_container_width=True
    )


# =====================================
# FOOTER
# =====================================

st.divider()

st.caption(
    "🛟 RepoRescue AI | Approved repairs are limited to the bundled sample project."
)

