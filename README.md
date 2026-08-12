# LEX REGIS

LEX REGIS is an enterprise-grade AI-powered Legal Technology Platform allowing citizens, lawyers, and administrators to securely manage legal cases from registration until closure.

## Architecture Overview

This platform utilizes a robust modular monolithic architecture powered by Django. It encapsulates domain logic within deeply structured apps and supports enterprise-grade configurability. The architecture decouples business logic from views, using services and selectors, and is pre-configured to handle seamless scaling. It serves as the foundational infrastructure for adding complex features such as AI, ML, and Blockchain later on.

## Folder Structure

```text
lex_regis/
├── apps/                 # Modular Django apps
│   ├── common/           # Cross-app utilities, shared mixins, exceptions, and base classes
│   ├── accounts/         # User and profile management
│   ├── cases/            # Legal case management domain
│   ├── documents/        # Document uploads and parsing
│   ├── dashboard/        # Administrative dashboards
│   └── (ai, ml, blockchain, notifications) # Future integrations
├── config/               # Project configuration (settings split into base, dev, prod, local)
├── docs/                 # Extensive documentation (SRS, ATDD, Architecture, API, etc.)
├── logs/                 # Segregated logs (application, security, api, errors)
├── media/                # Organized user uploads (documents, profiles, blockchain receipts)
├── requirements/         # Split dependencies (base, development, production)
├── scripts/              # Setup, backup, and automation scripts
├── static/               # Source static files (CSS, JS)
├── staticfiles/          # Collected static files (ignored in git)
├── templates/            # Global HTML templates
└── tests/                # Global test suites (unit, integration, api, performance)
```

## Development Workflow

1. **Local Settings**: Create `config/settings/local.py` to override shared configurations (already set to default to `.development`).
2. **Environment**: Copy `.env.example` to `.env` and configure local variables.
3. **Run Server**: Use `manage.py runserver` pointing by default to your local config.

## Coding Standards

- **PEP8 Compliance**: All Python code must strictly follow PEP8.
- **Type Hinting**: Use robust type hints for all function signatures (models, services, selectors) to enforce maintainability.
- **Modularity**: Domain logic belongs in `services/` (writes) and `selectors/` (reads), not directly inside Views or Models.
- **Single Responsibility Principle**: Ensure each Python file under an app structure handles exactly one concern (e.g. `accounts/models/user.py`).
- **Comments**: Write self-documenting code; use comments only to clarify non-obvious business intent.

## Branching Strategy

- **main**: Represents production-ready code.
- **develop**: The active development branch.
- **feature/name-of-feature**: Used for building new features. Must merge into `develop`.
- **hotfix/description**: Used for fixing critical issues on `main`.

## Future Roadmap

The platform structure is established. Upcoming modules will integrate seamlessly into their designated app directories:
- **Artificial Intelligence (AI)**: For case analysis and auto-suggestions.
- **Machine Learning (ML)**: Predictive legal modeling.
- **Blockchain**: For verifiable, immutable document timestamps and legal receipts.
