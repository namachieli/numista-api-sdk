# Changelog

## 0.1.0
### Changes
- None

### Additions
- Initial development
- Methods for API interaction
- Methods for ease of use
- OAuth capabilities for creation of Tokens to interact with User data
- Schema interpreters to help with payload formatting of POST/PATCH operations
- Auto generated code documentation
- Automated Linting (Super Linter)

### Deferred
- Payload schemas are 'Example' versions only. Future: Full schema ingestion parsing
- Body Payload validation is only validating the body exists for POST/PATCH. Future: Validate against ingested Schema and inform of granular errors
- Log level is either INFO (default) or DEBUG (bool). Future: Enable the changing of log levels before and after instantiation.
- Log path is not validated for existence, let alone iswritable(). Future: Path validation for log file location
- API Keys and Tokens are being explicitely obfuscated in logs. Future: Use log filters to automate obfuscation of sensitive data from logs
