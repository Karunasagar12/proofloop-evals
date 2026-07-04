# Security Notes

Proofloop Evals is a local evaluation tool. The MVP does not call model APIs, execute untrusted code, or send suite data to external services.

## Current safeguards

- Test suites are read from local YAML files.
- HTML reports escape user-provided input/output text.
- Generated reports are local artifacts and ignored by git.
- `.env` files are ignored by git.
- No API keys or model credentials are required for the MVP.

## Before using with live AI systems

- Treat model outputs and retrieved documents as untrusted text.
- Do not paste secrets into eval fixtures.
- Review generated reports before publishing them.
- Add provider-specific redaction before logging production outputs.

Please report security concerns privately to the maintainer.
