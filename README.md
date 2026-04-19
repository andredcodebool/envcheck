# envcheck

> CLI tool to audit and validate environment variable configs across services

---

## Installation

```bash
pip install envcheck
```

Or with [pipx](https://pypa.github.io/pipx/):

```bash
pipx install envcheck
```

---

## Usage

Define your expected environment variables in a `.env.schema` file:

```
DATABASE_URL=required
DEBUG=optional
PORT=required
```

Then run `envcheck` against your environment or a `.env` file:

```bash
# Check current environment
envcheck validate

# Check a specific .env file
envcheck validate --file .env.production

# Audit multiple services
envcheck audit --dir ./services
```

Missing or misconfigured variables will be reported with clear, actionable output:

```
[FAIL] DATABASE_URL — required but not set
[WARN] DEBUG — not defined in schema
[OK]   PORT — present
```

---

## Options

| Flag | Description |
|------|-------------|
| `--file` | Path to a `.env` file to validate |
| `--dir` | Directory to scan for `.env` files |
| `--strict` | Exit with non-zero code on warnings |
| `--quiet` | Suppress passing checks |

---

## License

MIT © [envcheck contributors](https://github.com/yourname/envcheck)