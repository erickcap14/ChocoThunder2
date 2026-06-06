# Python Code Standards

> This file defines the human-readability standard for Python files in this project.
> Both the audit and format specialists read this file to determine what to check and apply.
> Customize this file to match your conventions before running the Code Cleaner.

---

## 1) File Header

Every `.py` file must begin with a header block that describes the module.

**Format:**
```python
"""
<Module Name>

<One or two sentence description of what this file does and why it exists.>

Author: <Name>
Version: <X.Y.Z>
"""
```

**Rules:**
- Must be the very first statement in the file (before imports)
- Use triple double-quotes `"""`
- Include module name, description, author, and version
- Description should answer: "what does this file do?"

---

## 2) Import Organization

Imports must be grouped in this order, each group separated by a blank line:

```python
# 1. Standard library
import os
import sys

# 2. Third-party packages
import requests
import pandas as pd

# 3. Local/project modules
from myproject import utils
from .helpers import parse_input
```

**Rules:**
- No mixing of groups
- Alphabetical within each group (recommended)
- No wildcard imports (`from x import *`)

---

## 3) Constants

Constants must be:
- **UPPERCASE with underscores** (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- Defined **after imports and before any function definitions**
- Grouped together under an optional comment `# --- Constants ---`

**Format:**
```python
# --- Constants ---
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
BASE_URL = "https://api.example.com"
```

**Rules:**
- No magic numbers scattered through functions — extract them as constants
- Boolean flags: `ENABLE_LOGGING = True`

---

## 4) Section Separators

Use `###` separator lines to divide the file into logical sections.

**Required separators:**
```python
### Public Functions ###


### Private Functions ###
```

**Rules:**
- One blank line before the separator, two blank lines after (before first function)
- Public functions (no leading underscore) go above the private separator
- Private/helper functions (leading underscore `_`) go below
- Additional sections allowed (e.g., `### Utility Functions ###`, `### Class Definitions ###`)

---

## 5) Function Docstrings

Every function must have a triple-quote docstring immediately after the `def` line.

**Format:**
```python
def process_data(input_path, max_rows=None):
    '''
    Loads and processes raw data from a CSV file.

    Args:
        input_path (str): Path to the input CSV file.
        max_rows (int, optional): Maximum number of rows to load. Defaults to None (all rows).

    Returns:
        pd.DataFrame: Cleaned dataframe with normalized column names.
    '''
    ...
```

**Rules:**
- Use single triple-quotes `'''` (not `"""`)
- First line: one-sentence summary of what the function does
- Blank line after summary, then `Args:` block (if any parameters)
- `Returns:` block describing the return type and value
- If the function raises exceptions, add a `Raises:` block
- One-liner functions with no args/returns may use a single-line docstring: `'''Brief description.'''`

---

## 6) Type Hints

Type hints are **recommended** on all function signatures.

**Format:**
```python
def fetch_user(user_id: int, include_metadata: bool = False) -> dict:
```

**Rules:**
- Required for public functions (surfaced as a warning in audit if missing)
- Optional for private/internal helpers
- Use `Optional[X]` or `X | None` for nullable params

---

## 7) Main Guard

Any `.py` file intended to be run directly must include a main guard at the bottom.

**Format:**
```python
if __name__ == "__main__":
    main()
```

**Rules:**
- Must be the last block in the file
- Entry-point logic goes in a `main()` function, not directly under the guard
- Library/utility files (not meant to be run directly) do not need this
