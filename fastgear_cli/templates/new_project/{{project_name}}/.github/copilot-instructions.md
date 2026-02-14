# Python Development Guidelines

## 1. General Development Rules
1. Follow **PEP 8**
2. **Type‑hint everything** (functions, methods, attrs).<br>
   _unless the type is already explicit and unambiguous from the assignment itself_ (e.g., `app: FastAPI = FastAPI()` is redundant)
3. **One logical concept per file**, one public class per module, < 400 LOC.
4. **Functions ≤ 50 physical lines** and ≤ 6 cyclomatic complexity.
5. **Never catch bare** `Exception`. Catch the narrowest concrete exception, re‑raise with context (raise from).
6. **Prefer structured logging** over `print`.

## 2. Naming Conventions

| Element                  | Style                      |
|:-------------------------|:---------------------------|
| **Packages/Modules**     | `snake_case`               |
| **Classes / Exceptions** | `PascalCase`               |
| **Functions / Methods**  | `snake_case` + _verb‑noun_ |
| **Variables**            | `snake_case` + nouns       |
| **Constants / Enums**    | `UPPER_SNAKE_CASE`         |
| **Private**              | leading underscore         |

**Pronounceable ≥ 3 chars, avoid abbreviations** (use `response` not `res`). Align acronyms to lowercase (e.g. `http_client`).

## 3. Abstraction & Design
- **SRP** (Single Responsibility Principle)
- **Composition > Inheritance** for extensibility.

## 4. Testing Rules

| Guideline       | Rule                                                                                                                                                                                                                   |
|:----------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Structure**   | Mirror src tree:` src/foo/bar.py` → `tests/foo/test_bar.py`.<br/>Inside each test file declare **one** `Test<Subject>` **class per responsibility** (e.g. `class TestBar:`).<br/>Store **unit tests** in `tests/unit`. |
| **Naming**      | **Class:** class `Test<Subject>`.<br/>**Method:** `test_<expected_behavior>()` e.g. `test_add_user_saves_to_db`.                                                                                                       |
| **Focus**       | One behaviour per test method. Avoid application logic inside tests.                                                                                                                                                   |
| **Fixtures**    | Use `@pytest.fixture` and for data setup.<br/>Place fixture modules in a `fixtures` directory that **mirrors the source tree** — e.g. `src/foo/bar.py` → `tests/fixtures/foo/bar_fixtures.py`.                         |
| **Parametrize** | Use`pytest.mark.parametrize` instead of loops.                                                                                                                                                                         |
| **Isolation**   | Mock external services with `pytest-mock` or `responses`.                                                                                                                                                              |

## 5. Documentation
> Generate docstrings **only when I explicitly request them**
In every other situation, do not add docstrings, block comments, or extra READMEs.

### Required docstring layout (Google Style)
```python
def example(param1: int, param2: str) -> bool:
    """One‑line summary in the imperative mood.

    Optional extended description in additional paragraph(s)
    when it adds real value—don’t restate the obvious.

    Args:
        param1 (int): Brief description.
        param2 (str): Brief description.

    Returns:
        bool: Meaning of the return value.

    Raises:
        ValueError: Condition that raises the exception.

    Examples:
        >>> example(1, "x")
        True
    """
    ...
```

1. **Summary:** first line ≤ 72 characters, no ending period.
2. **Detailed description:** include only if it helps comprehension.
3. **Allowed sections (exact order) –** `Args`, `Returns`, `Yields`, `Raises`, `Examples`, `Notes`.
4. **Typing:** put the type in parentheses, aligned with the argument name.
5. **Spacing:** one blank line before every section header.

### Additional conventions
- **Language:** always in **English**.
- **Length:** keep the docstring proportional to complexity.
- **Inline comments (`# …`):** use only when strictly necessary.
- **Sync:** update the docstring after a signature or logic change.

## 6. Other Coding Guidelines
- **Use `# TODO:` comments** to mark unfinished or placeholder logic.
    - Place the `# TODO:` comment **immediately above** or **inline with** the incomplete code block.
    - Keep the comment brief and action‑oriented (prefer verbs such as _handle_, _implement_, _optimize_).
    - Remove or update the TODO once the logic is finalized.