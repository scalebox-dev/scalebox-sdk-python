# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take security bugs seriously. We appreciate your efforts to responsibly disclose your findings, and will make every effort to acknowledge your contributions.

### How to Report a Security Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following methods:

1. **Email**: Send details to security@scalebox.dev
2. **GitHub Security Advisory**: Use GitHub's private vulnerability reporting feature
3. **Encrypted Communication**: Use our PGP key for sensitive information

### What to Include

When reporting a vulnerability, please include:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if any)
- Your contact information

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution**: As quickly as possible, typically within 30 days

### Recognition

We maintain a security hall of fame to recognize security researchers who help keep ScaleBox secure. Contributors will be listed (with permission) in our security acknowledgments.

## Security Best Practices

### For Users

1. **Keep Dependencies Updated**: Regularly update your dependencies
2. **Use Environment Variables**: Store API keys in environment variables, not in code
3. **Validate Input**: Always validate user input before processing
4. **Use HTTPS**: Always use HTTPS for API communications
5. **Monitor Usage**: Keep track of your API usage and set up alerts

### For Developers

1. **Code Review**: All code changes must be reviewed
2. **Security Testing**: Include security tests in your test suite
3. **Dependency Scanning**: Use tools to scan for vulnerable dependencies
4. **Secrets Management**: Never commit secrets or API keys
5. **Input Validation**: Validate all inputs from external sources

## Security Features

### Authentication
- API key-based authentication
- Token-based authentication with expiration
- Support for custom authentication headers

### Data Protection
- All communications encrypted with TLS 1.2+
- No persistent storage of user code or data
- Automatic cleanup of sandbox environments

### Network Security
- Rate limiting to prevent abuse
- IP whitelisting support
- Request signing for additional security

## Vulnerability Disclosure

When we discover a security vulnerability, we will:

1. **Assess the Impact**: Determine the severity and scope
2. **Develop a Fix**: Create a patch to address the vulnerability
3. **Coordinate Disclosure**: Work with security researchers on coordinated disclosure
4. **Release Update**: Publish a new version with the fix
5. **Notify Users**: Communicate the issue and resolution to users

## Contact Information

- **Security Team**: security@scalebox.dev
- **General Support**: support@scalebox.dev
- **PGP Key**: Available upon request

## Security Updates

Subscribe to our security mailing list to receive notifications about security updates and vulnerabilities.

---

*This security policy is effective as of the date of publication and may be updated periodically.*
