# Contributing to VibeAgent

Thank you for your interest in contributing to VibeAgent! We welcome contributions from the community.

## 🤔 Quick Answer: What Happens When You Review a Pull Request?

**Reviewing a pull request does NOT delete the work!** 

When you review a PR:
- ✅ The code stays in the PR branch
- ✅ Your feedback is added as comments
- ✅ The author can make changes based on your review
- ✅ Nothing is merged or deleted until explicitly approved and merged

### Pull Request Lifecycle

1. **PR Created** → Code is in a separate branch, main code is untouched
2. **Review Requested** → Reviewers examine the changes
3. **Feedback Given** → Comments and suggestions are added
4. **Changes Made** (if needed) → Author updates the PR
5. **Approved** → Reviewers approve the changes
6. **Merged** → Code is added to the main branch (this is when it becomes part of the main codebase)
7. **Branch Deleted** (optional) → The PR branch can be safely deleted after merge

**Important**: Only when a PR is **merged** does the code become part of the main codebase. Until then, it remains isolated in its own branch.

## 🚀 How to Contribute

### Types of Contributions We Welcome

- 🐛 **Bug fixes**: Found a bug? Submit a fix!
- ✨ **New features**: Have an idea? Let's discuss it first in an issue
- 📚 **Documentation**: Improve guides, fix typos, add examples
- 🧪 **Tests**: Add test coverage for existing features
- 🎨 **UI improvements**: Make the web interface even better

### Getting Started

1. **Fork the repository**
   ```bash
   # Click "Fork" button on GitHub
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/vibeagent.git
   cd vibeagent
   ```

3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Make your changes**
   - Write clear, readable code
   - Follow the existing code style
   - Add tests if applicable
   - Update documentation if needed

6. **Test your changes**
   ```bash
   python test_vibeagent.py
   ```

7. **Commit your changes**
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

8. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

9. **Create a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template
   - Submit!

## 📝 Pull Request Guidelines

### Before Submitting

- [ ] Code follows the project style
- [ ] Tests pass (`python test_vibeagent.py`)
- [ ] Documentation is updated (if needed)
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains what and why

### PR Description Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (describe)

## Testing
How did you test these changes?

## Related Issues
Fixes #(issue number)
```

## 🔍 Code Review Process

### For Contributors (PR Authors)

1. **Submit your PR** with a clear description
2. **Wait for review** (usually within 1-3 days)
3. **Respond to feedback** - reviewers may request changes
4. **Make requested changes** and push new commits
5. **Request re-review** after addressing feedback
6. **Merge** happens after approval (maintainer will merge)

### For Reviewers

1. **Review the code** - check logic, style, tests
2. **Leave constructive feedback** - be helpful and kind
3. **Request changes** if needed, or **Approve** if good
4. **Never force-merge** without approval

**Remember**: Reviews are collaborative! The goal is to improve the code together.

## 🎯 What Gets Merged?

After a PR is reviewed and approved:

1. **Maintainer merges** the PR into the `main` branch
2. **Code becomes part of the project** - now everyone can use it
3. **PR branch can be deleted** - it's no longer needed
4. **Changes are in the next release** - users get your improvements

The work is **never deleted** - it becomes part of the permanent codebase!

## 🛠️ Development Setup

### Environment Setup

```bash
# Clone your fork (or the main repo)
git clone https://github.com/YOUR_USERNAME/vibeagent.git
cd vibeagent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings
```

### Running Tests

```bash
# Run all tests
python test_vibeagent.py

# Test web interface manually
python -m vibeagent.cli web
# Open http://localhost:5000
```

### Code Style

- **Python**: Follow PEP 8 style guidelines
- **Line length**: 100 characters max
- **Imports**: Group standard library, third-party, and local imports
- **Comments**: Use for complex logic, not obvious code
- **Type hints**: Use where helpful (not required everywhere)

## 🐛 Reporting Bugs

### Before Reporting

1. **Check existing issues** - someone might have reported it already
2. **Update to latest version** - bug might be fixed
3. **Check documentation** - might be expected behavior

### Bug Report Template

```markdown
**Describe the bug**
Clear description of what's wrong

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen

**Environment**
- OS: [e.g., Windows 10, macOS 12, Ubuntu 22.04]
- Python version: [e.g., 3.9.5]
- VibeAgent version: [e.g., 1.0.0]

**Additional context**
Screenshots, error messages, etc.
```

## 💡 Feature Requests

We love new ideas! Before submitting:

1. **Check existing issues** - might already be planned
2. **Start a discussion** - create an issue to discuss first
3. **Be specific** - explain the use case and benefits

### Feature Request Template

```markdown
**Feature description**
What feature would you like?

**Use case**
Why is this useful?

**Proposed solution**
How might this work?

**Alternatives**
Other ways to solve this?
```

## 🏗️ Project Structure

```
vibeagent/
├── vibeagent/              # Main package
│   ├── agent.py            # Core AI agent logic
│   ├── avocado_integration.py  # Avocado wallet integration
│   ├── cli.py              # Command-line interface
│   ├── web_interface.py    # Flask web server
│   └── templates/          # HTML templates
├── contracts/              # Solidity smart contracts
├── docs/                   # Documentation
├── examples/               # Usage examples
└── tests/                  # Test files
```

## 📜 Coding Guidelines

### Python Best Practices

```python
# Good: Clear function names
def calculate_arbitrage_profit(token_a, token_b, amount):
    """Calculate potential profit from arbitrage opportunity."""
    # implementation

# Bad: Unclear names
def calc(a, b, x):
    # what does this do?
```

### Documentation

- **Docstrings**: Add for all public functions/classes
- **Comments**: Explain "why", not "what"
- **README**: Update if adding user-facing features

## 🤝 Community Guidelines

### Be Respectful

- Welcome beginners
- Be patient with questions
- Give constructive feedback
- Assume good intentions

### Be Helpful

- Answer questions when you can
- Share knowledge generously
- Help review PRs
- Improve documentation

## 📞 Getting Help

- 📖 **Documentation**: Check README.md and docs/
- 💬 **Discord**: Join our community (link in README)
- 🐛 **Issues**: Search or create GitHub issues
- 📧 **Email**: For security issues only

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## ✅ Checklist for First-Time Contributors

- [ ] Read this guide
- [ ] Fork the repository
- [ ] Create a branch for your changes
- [ ] Make your changes
- [ ] Test your changes
- [ ] Commit with clear messages
- [ ] Push to your fork
- [ ] Create a Pull Request
- [ ] Respond to review feedback
- [ ] Celebrate your contribution! 🎉

---

**Thank you for contributing to VibeAgent!** Your work helps make DeFi accessible to everyone. 🚀
