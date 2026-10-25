# RepoRescue AI

Streamlit demo for controlled repair of the bundled calculator sample project.

## Install and run

```sh
python -m pip install -r requirements.txt
streamlit run app.py
```

Failproof AI tracing is optional until the Python SDK is installed. The SDK
records the custom agent session and its real event/session ID; it does not
provide policy evaluation for this Streamlit runtime. The UI therefore reports
policy outcome as `NOT EVALUATED` and does not present tracing as enforcement.

## Failproof AI Cloud setup

For Cloud delivery, use the official [custom-agent guide](https://docs.befailproof.ai/reference/custom-agents): create a machine key with
`events:add`, configure the Failproof daemon, and provide the key through the
`FAILPROOFAI_CLOUD_TOKEN` environment variable or a secret manager. Never place
the key in source control or a command-line argument. The key is not required
for local SDK instrumentation; Cloud delivery depends on daemon configuration.

The documented SDK package is `failproofai-sdk` (Python import
`failproofai_sdk`). The documented CLI setup is `npm install -g failproofai`,
then `failproofai config`; use `failproofai config --status` to inspect actual
connection and daemon state. This app does not run those setup commands.

## Policy enforcement limitation

Failproof's official docs state that a custom runtime must expose actions before
execution, send structured input to the policy engine, and apply the resulting
allow/instruct/deny decision; they direct custom-runtime owners to contact
`support@befailproof.ai` to map and validate the integration. Until that runtime
hook is designed and validated, RepoRescue keeps its own human approval,
project-boundary, patch-content, and stale-file safeguards and reports no
Failproof policy verdict.
