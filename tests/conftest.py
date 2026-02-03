"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def sample_vault() -> Path:
    """Return path to sample vault fixture."""
    return Path(__file__).parent / "fixtures" / "sample_vault"


@pytest.fixture
def daily_note_path(sample_vault: Path) -> Path:
    """Return path to DailyNote.md."""
    return sample_vault / "DailyNote.md"


@pytest.fixture
def project_a_path(sample_vault: Path) -> Path:
    """Return path to ProjectA.md."""
    return sample_vault / "ProjectA.md"


@pytest.fixture
def daily_note_content() -> str:
    """Return content of DailyNote.md."""
    return """---
date: 2024-01-15
author: John
---

# Daily Note

Today I worked on [[ProjectA]] and [[ProjectB]].

Also reviewed the ![[Screenshot.png]] from the meeting.

#daily #work
"""


@pytest.fixture
def project_a_content() -> str:
    """Return content of ProjectA.md with code blocks."""
    return """---
status: active
priority: high
---

# Project A

This is the main project. See also [[ProjectB|Project B Link]].

## Code Example

```python
# This should NOT be parsed as a link
link = "[[NotALink]]"
tag = "#notAtag"
```

Inline code: `[[AlsoNotALink]]` should be ignored.

## References

- Related to [[DailyNote]]
- Embeds: ![[diagram.svg]]

#project #important #project/frontend
"""
