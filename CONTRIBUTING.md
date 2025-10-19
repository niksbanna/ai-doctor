# Contributing to AI Doctor

Thank you for your interest in contributing to AI Doctor! This document provides guidelines for contributing to the project.

## Important Note

⚠️ **Medical Safety First**: All contributions must maintain or enhance the safety features of the system. Any changes that could affect patient safety require extra scrutiny and testing.

## Types of Contributions

### 1. Bug Reports
- Use the issue tracker
- Describe the bug clearly
- Include steps to reproduce
- Note any medical safety implications

### 2. Feature Requests
- Explain the use case
- Consider safety implications
- Provide medical evidence if applicable

### 3. Code Contributions

#### Before You Start
- Check existing issues and PRs
- Discuss major changes first
- Ensure you understand medical coding standards (ICD-10, SNOMED CT, LOINC)

#### Development Process
1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

#### Code Standards
- Follow PEP 8 style guide
- Write clear docstrings
- Add type hints
- Include unit tests
- Maintain test coverage

#### Medical Safety Requirements
- Never remove or weaken safety checks
- Add tests for safety features
- Document medical reasoning
- Cite evidence where appropriate
- Always include verification disclaimers

### 4. Documentation
- Improve clarity
- Add examples
- Fix typos
- Enhance medical explanations

## Pull Request Process

1. **Update tests**: Add tests for new features
2. **Update documentation**: Reflect changes in README and docstrings
3. **Pass all tests**: Ensure `pytest` passes
4. **Medical review**: For medical logic changes, note this in PR
5. **Code review**: Wait for maintainer review

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=ai_doctor tests/

# Run examples
python examples.py
```

## Medical Accuracy

When contributing medical logic:
- Cite reputable sources
- Use established guidelines
- Be conservative in recommendations
- Emphasize need for professional verification

## Code of Conduct

- Be respectful and professional
- Focus on patient safety
- Provide constructive feedback
- Remember this affects healthcare

## Questions?

Open an issue for:
- Clarification on contribution process
- Medical coding questions
- Architecture decisions
- Feature discussions

## License

By contributing, you agree that your contributions will be licensed under the MIT License (see LICENSE file) with the medical disclaimer.
