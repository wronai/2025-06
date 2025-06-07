# Security Policy

## Supported Versions

We provide security updates for the following versions of Weekly:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take security issues in Weekly seriously. We appreciate your efforts to responsibly disclose your findings, and will make every effort to acknowledge your contributions.

To report a security issue, please email info@softreck.dev with the subject line "[SECURITY] Weekly Vulnerability Report".

### When to report a security issue?
- You think you discovered a potential security vulnerability in Weekly
- You are unsure how a vulnerability affects Weekly
- You think you discovered a vulnerability in another project that our project depends on (e.g., Python, pip, etc.)

### When not to report a security issue?
- You need help applying security related updates
- Your issue is not security related

### Security email content
Please include the following details in your email:
- A description of the vulnerability
- Steps to reproduce the issue
- Any special configuration required to reproduce the issue
- Proof-of-concept or exploit code (if available)
- Impact of the issue, including how an attacker might exploit the issue
- Your name and affiliation (if any)

## Our Security Process

1. Upon receiving a security report, we will acknowledge receipt within 3 business days
2. We will confirm the issue and determine the affected versions
3. We will audit code to find any potential similar problems
4. We will prepare fixes for all releases still under maintenance
5. We will coordinate the release of security advisories and updates

## Public Disclosure Process

1. Security vulnerabilities will be disclosed through GitHub Security Advisories
2. For each vulnerability, we will publish a security advisory after a fix is available
3. The advisory will be credited to the reporter (unless they wish to remain anonymous)
4. We will announce vulnerabilities on our GitHub repository and other appropriate channels

## Security Updates and Alerts

Security updates will be released as patch versions (e.g., 1.2.3) for all supported versions. We recommend always running the latest patch version of Weekly.

## Security Best Practices

### For Users
- Always keep your Python environment and dependencies up to date
- Only install packages from trusted sources
- Review the permissions and access controls of your project directories
- Use virtual environments to isolate project dependencies

### For Developers
- Never include sensitive information in version control
- Use environment variables for configuration
- Keep all dependencies up to date
- Follow the principle of least privilege
- Write and maintain tests for security-critical code

## Security Related Configuration

Weekly can be configured with the following security-related settings:

- `MAX_FILE_SIZE`: Maximum file size to process (default: 10MB)
- `ALLOWED_FILE_TYPES`: Whitelist of allowed file extensions
- `DISABLE_NETWORK`: Disable all network operations (default: False)
- `SANDBOX_MODE`: Run in a more restricted mode (default: True)

## Credits

We would like to thank all security researchers and users who report security vulnerabilities to us. Your efforts help us make Weekly more secure for everyone.
