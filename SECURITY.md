# TerminalCoin Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Security Features

TerminalCoin implements the following security best practices:

### 1. **Input Validation**

- All user inputs and API responses are validated using Pydantic models
- URL validation for news feeds
- Coin ID format validation
- Data sanitization to prevent injection attacks

### 2. **Rate Limiting**

- API rate limiting to prevent abuse
- Configurable limits for API calls
- Automatic retry with exponential backoff

### 3. **Error Handling**

- Comprehensive exception handling
- No sensitive data in error messages
- Secure logging practices

### 4. **Network Security**

- HTTPS-only API connections
- Request timeouts to prevent hanging
- Certificate verification enabled
- User-Agent headers for identification

### 5. **Data Protection**

- No storage of sensitive user data
- No API keys required (public APIs only)
- Sanitized text output to prevent markup injection

### 6. **Dependencies**

- Minimal dependency footprint
- Regular dependency updates
- Use of well-maintained libraries

## Reporting a Vulnerability

If you discover a security vulnerability in TerminalCoin, please report it by:

1. **DO NOT** open a public issue
2. Email the maintainer directly (if available)
3. Provide detailed information about the vulnerability
4. Include steps to reproduce if possible

### What to Include

- Description of the vulnerability
- Potential impact
- Steps to reproduce
- Suggested fix (if available)
- Your contact information

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-3 days
  - High: 1-2 weeks
  - Medium: 2-4 weeks
  - Low: Next release cycle

## Security Best Practices for Users

1. **Keep Dependencies Updated**

   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Run in Isolated Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Monitor Logs**

   - Check `terminalcoin.log` for suspicious activity
   - Set appropriate log levels in production

4. **Network Security**
   - Use on trusted networks
   - Consider using a VPN if on public WiFi

## Known Security Considerations

### API Dependencies

- CoinGecko API: Public API, no authentication required
- RSS Feeds: Third-party content, sanitized before display

### Rate Limiting

- Default: 50 calls per 60 seconds
- Configurable in `config.py`

### Data Privacy

- No personal data collected
- No analytics or tracking
- All data fetched in real-time (no caching of sensitive info)

## Security Checklist for Contributors

- [ ] All inputs validated
- [ ] No hardcoded credentials
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies are up to date
- [ ] Code follows secure coding practices
- [ ] No eval() or exec() usage
- [ ] Proper exception handling
- [ ] Logging doesn't include sensitive data

## License

This security policy is part of the TerminalCoin project and follows the same license.
