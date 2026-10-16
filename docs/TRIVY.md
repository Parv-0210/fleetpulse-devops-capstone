# Trivy — what is scanned and what the result means

**What runs.** In `.github/workflows/ci-cd.yml`, after each image is built (and before it is pushed),
`aquasecurity/trivy-action` scans the image with `severity: HIGH,CRITICAL`, `ignore-unfixed: true` and
`exit-code: "1"`. Trivy inspects the OS package database (Debian `dpkg` status for the backend, Alpine
`apk` for the frontend) and language packages (Python `*.dist-info` in the backend's virtualenv, the
nginx image has none) and compares every installed version against its vulnerability database.
A second, non-blocking run writes SARIF for the GitHub Security tab and a CycloneDX SBOM artifact.

**What we found and fixed.** The first local scan reported:

| Image | Findings | Cause | Fix |
|---|---|---|---|
| backend | 4 HIGH (`setuptools` CVE-2025-47273, `urllib3` ×2, `msgpack`) | all belonged to `pip` and `setuptools` shipped in the base image / venv, not to the application | the runtime stage removes `pip`, `setuptools`, `wheel` and `ensurepip`; `apt-get upgrade` keeps Debian patched |
| frontend | 2 CRITICAL + 39 HIGH (`libssl3`, `libexpat`, `libpng`, `libxml2`, `zlib`, …) | the `1.27-alpine` nginx tag is based on Alpine 3.21 with stale packages | moved to `nginx-unprivileged:1.30-alpine-slim` (Alpine 3.24) and run `apk upgrade --no-cache` at build time |

After the fix both images report **0 HIGH / 0 CRITICAL**, so the gate passes and the push step runs.

**What a clean result means.** No *known, fixable* vulnerability of HIGH or CRITICAL severity exists in
the packages inside the image at scan time. It does not prove the application code is secure (that needs
SAST, dependency review and runtime controls), and new CVEs are published daily, so the scan is repeated
on every pipeline run and base images are rebuilt regularly. `ignore-unfixed` intentionally skips CVEs
that have no vendor patch yet, because failing on them would block every release without a possible fix.
