# 🤝 Contributing to OpenWebUI MCP Setup

Thank you for considering contributing to this project! We welcome contributions from everyone, whether you're fixing a typo or adding a major feature.

## 🚀 Quick Start for Contributors

### Ways to Contribute

1. **🐛 Report Bugs**: Found something broken? Let us know!
2. **💡 Suggest Features**: Have an idea for improvement? Share it!
3. **📖 Improve Documentation**: Help make our guides clearer
4. **🔧 Submit Code**: Fix bugs or add new features
5. **🧪 Test Configurations**: Try setups on different systems
6. **🌍 Add Examples**: Share your working configurations

### Before You Start

- Check existing [Issues](../../issues) and [Pull Requests](../../pulls) to avoid duplicates
- For major changes, open an issue first to discuss the approach
- Test your changes on at least one platform (Windows, Mac, or Linux)

## 📋 Types of Contributions We Need

### 🔥 High Priority
- **More MCP Server Examples**: Support for additional MCP servers
- **Platform-Specific Fixes**: Windows, Mac, Linux compatibility issues
- **Error Handling**: Better error messages and recovery
- **Security Improvements**: Enhanced security configurations

### 📚 Documentation
- **Beginner Guides**: Simplify complex concepts
- **Video Tutorials**: Screen recordings of setup processes
- **Translation**: Guides in other languages
- **FAQ Updates**: Common questions and answers

### 🛠️ Code Contributions
- **New Configuration Templates**: Additional use cases
- **Testing Scripts**: Better validation and monitoring
- **Docker Improvements**: More deployment options
- **Bug Fixes**: Fix reported issues

## 🔧 Development Setup

### Prerequisites
- Git
- Python 3.8+ (for scripts)
- Docker (for testing containers)
- Basic knowledge of MCP, MCPO, and Open Web UI

### Local Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/openwebui-mcp-setup.git
cd openwebui-mcp-setup

# Test the examples
cd examples
./time-server.sh  # Linux/Mac
# or
time-server.bat   # Windows

# Validate configurations
cd ../scripts
python3 validate-config.py --check-all

# Run health checks
python3 health-check.py
```

## 📝 Contribution Guidelines

### Code Style
- **Shell Scripts**: Use `#!/bin/bash` and `set -e`
- **Batch Files**: Include error handling and clear output
- **Python**: Follow PEP 8, include type hints where helpful
- **JSON**: Use 2-space indentation, validate syntax
- **Markdown**: Use clear headings, code blocks, and examples

### Commit Messages
Use clear, descriptive commit messages:
```
feat: add support for mcp-server-web
fix: resolve Windows path issues in examples
docs: improve troubleshooting guide
test: add validation for filesystem server config
```

### Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Keep changes focused and atomic
   - Add/update documentation as needed
   - Test on your platform

3. **Test Your Changes**
   ```bash
   # Test configurations
   python3 scripts/validate-config.py --check-all
   
   # Test examples (if modified)
   cd examples && ./time-server.sh
   
   # Run health checks
   python3 scripts/health-check.py
   ```

4. **Submit Pull Request**
   - Use a clear title and description
   - Reference any related issues
   - Include testing steps
   - Add screenshots for UI changes

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] 📖 Documentation update
- [ ] 🔧 Configuration improvement
- [ ] 🧪 Test addition

## Testing
- [ ] Tested on Windows
- [ ] Tested on Mac
- [ ] Tested on Linux
- [ ] Tested with Docker
- [ ] Configuration validates
- [ ] Scripts run successfully

## Screenshots (if applicable)

## Additional Notes
Any other context about the changes
```

## 🧪 Testing Guidelines

### Manual Testing Checklist
- [ ] Configuration files validate without errors
- [ ] Example scripts run successfully
- [ ] MCPO starts and responds to requests
- [ ] Open Web UI can connect to tools
- [ ] Tools function as expected in chat
- [ ] Health checks pass
- [ ] Documentation is accurate

### Automated Testing
We welcome contributions to improve our testing:
- Unit tests for validation scripts
- Integration tests for configurations
- GitHub Actions workflows
- Cross-platform compatibility tests

## 📋 Issue Reporting

### Bug Reports
Include:
- **Operating System**: Windows 10, macOS 13, Ubuntu 22.04, etc.
- **Setup Method**: Examples, Docker, manual configuration
- **Error Messages**: Full error output
- **Steps to Reproduce**: Exact commands used
- **Expected vs Actual Behavior**
- **Configuration Files**: Sanitized (remove secrets)

### Feature Requests
Include:
- **Use Case**: What problem does this solve?
- **Proposed Solution**: How should it work?
- **Alternatives Considered**: Other approaches
- **Additional Context**: Examples, mockups, etc.

## 🎯 Areas Needing Help

### High-Impact, Beginner-Friendly
- **Documentation Improvements**: Fix typos, clarify instructions
- **Example Scripts**: Add more MCP server examples
- **Error Messages**: Make them more helpful
- **Platform Testing**: Test on different OS versions

### Advanced Contributions
- **Security Enhancements**: Production security features
- **Performance Optimizations**: Faster startup, better resource usage
- **Monitoring Integration**: Grafana, Prometheus, etc.
- **CI/CD Improvements**: Better automated testing

## 🌟 Recognition

Contributors are recognized in:
- README acknowledgments
- Release notes for significant contributions
- GitHub contributor graphs
- Special mentions for major features

## 📞 Getting Help

- **Questions**: Open a [Discussion](../../discussions)
- **Bugs**: Create an [Issue](../../issues)
- **Security**: Email maintainers directly
- **Ideas**: Share in [Discussions](../../discussions)

## 📜 Code of Conduct

### Our Standards
- **Be Respectful**: Treat everyone with kindness
- **Be Constructive**: Focus on improving the project
- **Be Inclusive**: Welcome newcomers and different perspectives
- **Be Patient**: Help others learn and grow

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or inflammatory comments
- Publishing private information
- Inappropriate content

### Enforcement
Maintainers will address violations by:
1. Warning the individual
2. Temporary suspension for repeated violations
3. Permanent ban for serious violations

Report violations to project maintainers.

## 🎉 Thank You!

Every contribution helps make this project better for everyone. Whether you:
- Fixed a typo
- Added a new feature
- Improved documentation
- Tested on a new platform
- Reported a bug

**You're making a difference!** 🙏

---

## 📚 Additional Resources

- [MCP Documentation](https://github.com/modelcontextprotocol)
- [MCPO Repository](https://github.com/open-webui/mcpo)
- [Open Web UI Documentation](https://docs.openwebui.com/)
- [Docker Best Practices](https://docs.docker.com/develop/best-practices/)

Happy contributing! 🚀