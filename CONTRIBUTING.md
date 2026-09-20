# Contributing to SAT-SA

Thank you for contributing to the **Supervisory Analytics Tool for SOC Assessment (SAT-SA)**.

## Engineering Principles
1. **Explainability Over Black-Box Complexity**: Every supervisory rule and statistical metric must provide explicit rationale, comparison baselines, and exact record citations.
2. **Air-Gap Strictness**: Never introduce external runtime network dependencies, cloud SDKs, or remote CDN links. All styles, scripts, and libraries must remain vendored or local.
3. **Auditability**: Any action that alters entity assessments, rules, or reviewer dispositions must be recorded in the append-only audit trail.

## Development Workflow
1. Clone the repository into your local development enclave.
2. Install local dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run tests before submitting changes:
   ```bash
   python -m pytest tests/ -v
   ```
4. Adhere to PEP 8 coding standards and type annotations.
