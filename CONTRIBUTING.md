# Contributing to IoT Predictive Maintenance Solution

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:

- **Clear title** describing the problem
- **Steps to reproduce** the bug
- **Expected behavior** vs actual behavior
- **Environment details**: Python version, OS, Azure/Fabric setup
- **Logs or screenshots** if applicable

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:

- **Clear description** of the proposed feature
- **Use case**: Why would this be useful?
- **Examples**: How would it work?
- **Impact**: Who would benefit?

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** with clear, descriptive commits:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```
4. **Test your changes** thoroughly
5. **Update documentation** if needed (README, docstrings, etc.)
6. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request** against the `main` branch

## 📝 Code Style Guidelines

### Python Code
- Follow **PEP 8** style guide
- Use **type hints** where appropriate
- Add **docstrings** to functions and classes
- Keep functions **small and focused** (single responsibility)
- Use **meaningful variable names**

Example:
```python
def calculate_remaining_rotations(current: float, max_capacity: float) -> float:
    """
    Calculate remaining rotations until bit replacement.
    
    Args:
        current: Current cumulative rotation count
        max_capacity: Maximum rotation capacity of the bit
        
    Returns:
        Remaining rotations before replacement needed
    """
    return max(0, max_capacity - current)
```

### Jupyter Notebooks
- Use **markdown cells** to explain each section
- Keep **code cells small** (one logical operation per cell)
- Add **comments** for complex logic
- **Clear outputs** before committing (reduce file size)
- **Test notebooks** end-to-end before submitting

### Documentation
- Use **clear headings** and structure
- Include **code examples** where helpful
- Add **screenshots** for UI-based steps
- Keep **language simple** and accessible
- Use **emojis sparingly** for visual clarity

## 🧪 Testing Guidelines

Before submitting a PR:

1. **IoT Simulator**:
   - Test with at least 1-3 devices
   - Verify telemetry sends successfully
   - Check hot-reload configuration works

2. **ML Pipeline**:
   - Run notebook end-to-end
   - Verify model trains successfully
   - Check predictions are reasonable
   - Validate MAE and R² metrics

3. **Power Platform**:
   - Test flows with sample data
   - Verify emails send correctly
   - Check Power Apps works on mobile
   - Validate data writes to backend

## 🎯 Areas for Contribution

We especially welcome contributions in these areas:

### High Priority
- [ ] Additional ML models (LSTM, Prophet, Survival Analysis)
- [ ] Advanced anomaly detection algorithms
- [ ] Real-time streaming ML with Fabric RT Intelligence
- [ ] Cost optimization strategies
- [ ] Performance benchmarking

### Medium Priority
- [ ] Additional visualizations for Power BI
- [ ] Custom connectors for other IoT platforms (AWS IoT, Google Cloud IoT)
- [ ] Integration with Azure Digital Twins
- [ ] Multi-language support (translations)
- [ ] Unit tests and integration tests

### Documentation
- [ ] Video tutorials
- [ ] Troubleshooting guides
- [ ] Best practices for production deployment
- [ ] Cost estimation calculator
- [ ] Performance tuning guides

### Nice to Have
- [ ] Docker containerization for IoT simulator
- [ ] Terraform/ARM templates for Azure resources
- [ ] CI/CD pipelines (GitHub Actions)
- [ ] Sample datasets from other industries
- [ ] Integration with Azure DevOps

## 🔒 Security

If you discover a security vulnerability, please email us directly instead of creating a public issue. Include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## 📜 Code of Conduct

### Our Standards

- **Be respectful** and inclusive
- **Welcome newcomers** and help them learn
- **Accept constructive criticism** gracefully
- **Focus on what's best** for the community
- **Show empathy** towards others

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling or deliberately disruptive behavior
- Publishing others' private information
- Any conduct that would be unprofessional

## 📞 Questions?

If you have questions about contributing:

- Check the [README](README.md) first
- Review existing [Issues](https://github.com/yourusername/iot-predictive-maintenance/issues)
- Ask in [Discussions](https://github.com/yourusername/iot-predictive-maintenance/discussions)

## ✅ Checklist Before Submitting PR

- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Changes are tested locally
- [ ] Commit messages are clear
- [ ] PR description explains what and why
- [ ] No sensitive data (keys, passwords) in code
- [ ] Large files excluded (check .gitignore)

---

**Thank you for contributing to making predictive maintenance accessible to everyone!** 🚀
