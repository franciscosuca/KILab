---
name: Replace Semantic Release Placeholders
description: Replace template placeholders like {{PYTHON_PKG_DIR}} in .releaserc.json files with real project values.
---

# Replace Semantic Release Placeholders

Use this skill when a `.releaserc.json` file contains template placeholders that must be replaced with project-specific values before semantic-release can run correctly.

## Common placeholders

- `{{PYTHON_PKG_DIR}}` — the Python package directory containing `__init__.py`.
- `{{JS_PKG_NAME}}` — the JavaScript/Node.js package name (for `package.json` based replacements).
- `{{DOCKER_IMAGE}}` — the container image name used in publishing steps.

## How to replace

1. Identify the target language from the template path:
   - `templates/py/.releaserc.json` → Python project
   - `templates/js/.releaserc.json` → Node.js project
2. Ask the user for the real value of each placeholder, or infer it from the repository structure:
   - For Python: locate the directory that contains `__init__.py` and a `__version__` string.
   - For Node.js: read `name` from `package.json`.
3. Replace every occurrence of the placeholder in the `.releaserc.json` file with the resolved value.
4. Keep the JSON structure and semantic-release plugin order unchanged.
5. Validate the resulting JSON is well-formed.

## Example

Given a Python project with this layout:

```
my_project/
  my_project/
    __init__.py
```

Replace:

```json
"{{PYTHON_PKG_DIR}}/__init__.py"
```

with:

```json
"my_project/__init__.py"
```

## Validation checklist

- [ ] All `{{...}}` placeholders have been removed from the file.
- [ ] The JSON still parses correctly.
- [ ] The `semantic-release-replace-plugin` `files` paths match real files in the project.
- [ ] The `@semantic-release/git` `assets` list includes the same files as the replacement plugin.
