# Contributing to Antarctic

Thank you for your interest in contributing to Antarctic! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

- Be respectful and professional
- Focus on constructive feedback
- Help maintain code quality
- Document your changes

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Node.js 14+ (for API development)
- Git
- Code editor (VS Code recommended)

### Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/Narfbach/antarctic-autoclicker.git
cd antarctic-autoclicker
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Node.js dependencies:
```bash
npm install
```

4. Set up environment variables:
```bash
copy .env.example .env
# Edit .env with your configuration
```

## Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical production fixes

### Making Changes

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes following the coding standards

3. Test your changes thoroughly

4. Commit with descriptive messages:
```bash
git commit -m "Add: Brief description of changes"
```

5. Push to your branch:
```bash
git push origin feature/your-feature-name
```

6. Create a Pull Request

## Coding Standards

### Python Code Style

Follow PEP 8 guidelines:

```python
# Good
def calculate_delay(interval_ms: float, compensation: float) -> float:
    """
    Calculate compensated delay.
    
    Args:
        interval_ms: Base interval in milliseconds
        compensation: Compensation value to subtract
        
    Returns:
        Compensated delay in milliseconds
    """
    return max(0.1, interval_ms - compensation)

# Bad
def calc(i,c):
    return i-c if i-c>0 else 0.1
```

**Key Points**:
- Use type hints
- Write docstrings for functions and classes
- Use descriptive variable names
- Keep functions focused and small
- Maximum line length: 100 characters

### JavaScript Code Style

Follow modern ES6+ standards:

```javascript
// Good
async function validateLicense(licenseKey, hwid) {
  const { data, error } = await supabase
    .from('licenses')
    .select('*')
    .eq('license_key', licenseKey)
    .single();
    
  if (error) throw error;
  return data;
}

// Bad
function validateLicense(licenseKey,hwid){
var data=supabase.from('licenses').select('*').eq('license_key',licenseKey).single()
return data
}
```

**Key Points**:
- Use `const` and `let`, avoid `var`
- Use async/await for asynchronous code
- Use template literals for strings
- Use arrow functions where appropriate
- Proper error handling

### Naming Conventions

**Python**:
- Classes: `PascalCase` (e.g., `LatencyCompensator`)
- Functions/Methods: `snake_case` (e.g., `get_compensated_delay`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RTT_MS`)
- Private members: `_leading_underscore` (e.g., `_record_ping`)

**JavaScript**:
- Functions: `camelCase` (e.g., `validateLicense`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- Files: `kebab-case` (e.g., `rate-limit.js`)

## Testing

### Running Tests

```bash
# Python tests
python -m pytest tests/

# API tests
npm test
```

### Writing Tests

```python
# test_latency.py
import pytest
from src.latency_compensator import LatencyCompensator

def test_compensation_calculation():
    compensator = LatencyCompensator()
    compensator.half_rtt_ms = 50.0
    compensator.compensation_enabled = True
    
    result = compensator.get_compensated_delay(100.0)
    assert result == 50.0
```

## Documentation

### Code Documentation

- All public functions must have docstrings
- Complex algorithms should have inline comments
- Update relevant documentation files when changing functionality

### Documentation Files

- `README.md` - Project overview and quick start
- `docs/API.md` - API endpoint documentation
- `docs/ARCHITECTURE.md` - System architecture
- `CONTRIBUTING.md` - This file

## Pull Request Process

1. **Update Documentation**: Ensure all documentation is updated
2. **Add Tests**: Include tests for new functionality
3. **Code Review**: Address all review comments
4. **Squash Commits**: Clean up commit history if needed
5. **Merge**: Maintainer will merge after approval

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
```

## Common Tasks

### Adding a New Feature

1. Create feature branch
2. Implement feature with tests
3. Update documentation
4. Submit pull request

### Fixing a Bug

1. Create bugfix branch
2. Write test that reproduces bug
3. Fix the bug
4. Verify test passes
5. Submit pull request

### Updating Dependencies

```bash
# Python
pip install --upgrade package-name
pip freeze > requirements.txt

# Node.js
npm update package-name
```

## Project Structure Guidelines

### Adding New Files

- **Python modules**: Place in `src/`
- **API endpoints**: Place in `api/`
- **Utilities**: Place in `tools/`
- **Documentation**: Place in `docs/`
- **Tests**: Place in `tests/`

### File Organization

```
src/
  ├── core/           # Core functionality
  ├── gui/            # GUI components
  ├── utils/          # Utility functions
  └── security/       # Security modules
```

## Security Considerations

### Sensitive Data

- Never commit API keys or passwords
- Use environment variables for secrets
- Add sensitive files to `.gitignore`

### Code Security

- Validate all user inputs
- Use parameterized queries
- Implement proper error handling
- Follow principle of least privilege

## Release Process

1. Update version number in relevant files
2. Update CHANGELOG.md
3. Create release branch
4. Test thoroughly
5. Create git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
6. Push tag: `git push origin v1.0.0`
7. GitHub Actions will build and create release

## Getting Help

- Check existing documentation
- Search existing issues
- Create new issue with detailed description
- Contact maintainers

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to Antarctic!
