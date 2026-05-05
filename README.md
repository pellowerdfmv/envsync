# envsync

> Lightweight utility to sync and validate `.env` files across project environments

---

## Installation

```bash
pip install envsync
```

---

## Usage

```bash
# Check that .env matches all keys defined in .env.example
envsync validate

# Sync missing keys from .env.example into .env
envsync sync

# Specify custom file paths
envsync sync --source .env.example --target .env.production
```

You can also use it directly in Python:

```python
from envsync import validate, sync

# Validate your environment file
missing = validate(source=".env.example", target=".env")
if missing:
    print(f"Missing keys: {missing}")

# Sync missing keys with empty placeholders
sync(source=".env.example", target=".env")
```

---

## How It Works

`envsync` compares a reference file (typically `.env.example`) against your active `.env` file and reports or fills in any missing keys. It never overwrites existing values — only adds missing entries as empty placeholders.

---

## Features

- ✅ Validate `.env` files against a reference template
- ✅ Auto-sync missing keys without touching existing values
- ✅ CLI and Python API support
- ✅ Zero dependencies

---

## License

[MIT](LICENSE) © 2024 envsync contributors