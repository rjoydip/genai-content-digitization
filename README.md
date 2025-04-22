# Python Starter

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![image](https://img.shields.io/pypi/v/uv.svg)](https://pypi.python.org/pypi/uv)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
[![CI](https://github.com/rjoydip/genai-content-digitization/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/rjoydip/genai-content-digitization/actions/workflows/ci.yml)

GenAI Project for Content Digitization

## 🚀 Features

- UV package manager for dependency management
- Docker support
- Ruff for code formatting and linting
- Pytest for testing
- Logging configuration

## 📋 Prerequisites

- Python 3.13+
- Docker Desktop
- UV package manager

## 🛠 Installation

1. Clone the repository:

-----

Install project dependencies:

```bash
uv sync
```

## Development

### Local Development

- Run UV application locally:

```bash
uv run uvstarter main:app --port 8000 --reload
```

- Run code formatting and linting:

```bash
uv run ruff format .
# or
uv run ruff check --fix
```

- Run typechecking:

```bash
uv run pyright
```

- Run tests:

```bash
uv run pytest
```

### Docker Development

Build and run the application in Docker:

```bash
docker build -t app .
docker run -p 8000:8000 app
```

## ⚙️ Configuration

- Project dependencies and settings are managed in `pyproject.toml`
- Ruff is configured for code formatting and linting
- Pytest is set up for testing
- Logging configuration is available for different environments

## 🌐 API Endpoints

- `GET /`: Returns a "Hello from UV!" message

## 🧪 Testing

Tests are located in the `tests/` directory. Run the test suite using:

```bash
uv run pytest
```

## 🔍 Project Structure

```txt
uv-ci-template/
|── main.py # UV application
├── tests/
│ └── tests.py # Test suite
├── Dockerfile # Docker configuration
├── pyproject.toml # Project configuration
├── uv.lock # Libs and dependencies
└── README.md
```

## 👥 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
