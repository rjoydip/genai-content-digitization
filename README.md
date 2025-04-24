# Python Starter

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![image](https://img.shields.io/pypi/v/uv.svg)](https://pypi.python.org/pypi/uv)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
[![CI](https://github.com/rjoydip/genai-extract-tiff-text-content/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/rjoydip/genai-extract-tiff-text-content/actions/workflows/ci.yml)

GenAI project to extract content from TIFF using Azure Vision & rectify spelling using Azure OpenAI

## 🚀 Features

- UV package manager for dependency management
- Docker support
- Ruff for code formatting and linting
- PostgresSQL using [NeonDB](https://neon.tech/docs/guides/python)
- [Azure AI Vision Service](https://azure.microsoft.com/en-us/products/ai-services/ai-vision)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)

## 📋 Prerequisites

- Python 3.13+
- Docker Desktop
- UV package manager

## Code flow 

```mermaid
flowchart TD
    subgraph initialization[Initialization]
        A[Load environment variables] --> B[Set up paths]
        B --> C[Validate required environment variables]
        C --> D[Load configuration from JSON]
        D --> E[Convert date strings to datetime objects]
    end

    subgraph client_setup[Client Setup]
        F[Initialize Vision API Client] 
        G[Initialize Azure OpenAI Client]
    end

    subgraph database_processing[Database Processing]
        H[Create connection pool] --> I[Acquire database connection]
        I --> J[Fetch article IDs based on criteria]
        J --> K{Any articles found?}
    end

    subgraph parallel_processing[Parallel Processing]
        L[Create processing tasks for each article]
        M[Run tasks concurrently with asyncio.gather]
    end

    subgraph process_image_function[Process Image Function]
        N[Read TIFF image] --> O{File exists?}
        O -->|No| P[Return error]
        O -->|Yes| Q[Analyze with Vision API]
        Q --> R[Extract caption]
        Q --> S[Extract OCR text content]
        S --> T[Process text with OpenAI]
        T --> U[Return structured results]
    end

    subgraph results_handling[Results Handling]
        V[Process each result]
        V --> W{Is result an exception?}
        W -->|Yes| X[Log error]
        W -->|No| Y{Has error field?}
        Y -->|Yes| Z[Log file not found]
        Y -->|No| AA[Display article info]
    end

    initialization --> client_setup
    client_setup --> database_processing
    K -->|No| END[Exit]
    K -->|Yes| parallel_processing
    parallel_processing --> results_handling

    L --> process_image_function
    M --> V
```

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
