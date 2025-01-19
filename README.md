# AI Interview System - Microservices Architecture

## Overview
This project implements an AI-powered interview system using a microservices architecture. Each component operates independently and communicates via gRPC, with MongoDB handling persistent storage of interview sessions and metrics.

## System Components

### Primary Services
- **Orchestrator Service** (Port 50051): Coordinates interview flow and agent interactions
- **Technical Evaluation Service** (Port 50052): Manages technical assessments and coding challenges
- **Behavioral Assessment Service** (Port 50053): Conducts behavioral and leadership evaluations
- **Consent & Compliance Service** (Port 50054): Handles verification and legal requirements
- **Metrics Collection Service** (Port 50055): Real-time performance tracking and analytics

### Support Services
- Question Management: Dynamic question selection and validation
- Transition Coordination: Smooth phase transitions and timing management
- Emergency Handler: Issue resolution and session recovery
- Feedback Compilation: Comprehensive evaluation reports

## Prerequisites

### Required Software
- Python 3.12 (via pyenv)
- Docker & Docker Compose
- MongoDB 6.0
- Node.js (for web interface)

### API Keys
- NVIDIA API key (for AI services)
- Daily.co API key (for video sessions)

## Local Development Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ifitsmanu/interviewers.git
   cd interviewers
   ```

2. **Python Environment Setup**
   ```bash
   # Install Python 3.12 via pyenv if not already installed
   pyenv install 3.12.0
   pyenv local 3.12.0
   
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.template .env
   
   # Generate secure keys (you can use Python)
   python -c "import secrets; print(f'JWT_SECRET={secrets.token_hex(32)}')"
   python -c "import secrets; print(f'ENCRYPTION_KEY={secrets.token_hex(32)}')"
   
   # Edit .env with your configuration and API keys
   ```

4. **MongoDB Setup**
   ```bash
   # Start MongoDB and other services
   docker-compose up -d
   
   # Verify MongoDB connection
   python -c "from interviewers.services.database import get_client; import asyncio; asyncio.run(get_client())"
   ```

5. **Start Individual Services**
   ```bash
   # Start Orchestrator Service
   python -m interviewers.services.orchestrator

   # Start Technical Evaluation Service
   python -m interviewers.services.technical

   # Start Behavioral Assessment Service
   python -m interviewers.services.behavioral

   # Start Consent Service
   python -m interviewers.services.consent

   # Start Metrics Service
   python -m interviewers.services.metrics
   ```

## Testing

### Setup Test Environment
```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Configure test environment
cp .env.template .env.test
# Edit .env.test with test configuration
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=interviewers tests/
```

## Development Workflow

### Git Rules and Automation

#### Branch Protection
- Main branch is protected and requires:
  - Passing CI checks (tests, linting, type checking)
  - At least one code review approval
  - No stale reviews (reviews are dismissed when new commits are pushed)
  - Branch is up to date with main

#### Automated Testing
- GitHub Actions automatically run on all PRs and pushes to main
- Tests include:
  - Unit tests and integration tests
  - Code coverage reporting
  - Linting (flake8)
  - Type checking (mypy)
- All tests must pass before merging

#### Automated Merging
- PRs are automatically merged when:
  - All required checks pass
  - Required approvals are received
  - PR has "automerge" label and no "work in progress" label
  - Changes are squashed for clean history
  - Branch is deleted after merge

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Document functions and classes
- Run pre-commit hooks:
  ```bash
  pre-commit install
  pre-commit run --all-files
  ```

### Making Changes
1. Create a feature branch:
   ```bash
   # Use descriptive names with format: feature/description
   git checkout -b feature/your-feature-name
   ```

2. Make changes and test locally:
   ```bash
   # Run linting
   flake8 src/interviewers
   
   # Run type checking
   mypy src/interviewers
   
   # Run tests
   pytest
   ```

3. Commit changes:
   ```bash
   # Check status and diff before committing
   git status
   git diff
   
   # Use conventional commit messages
   git add .
   git commit -m "feat: Description of changes"
   ```

4. Push and create PR:
   ```bash
   # Always push before creating PR
   git push origin feature/your-feature-name
   
   # Create PR using GitHub CLI
   gh pr create --title "Your PR title" --body "Description"
   
   # Wait for CI checks
   gh pr checks --watch
   ```

### Important Git Rules
1. NEVER force push to any branch
2. NEVER push directly to main branch
3. Keep PRs focused and reasonably sized
4. Always wait for CI checks before merging
5. Use squash merging for clean history
6. Delete branches after merging
7. Keep commit messages clear and descriptive

## Monitoring and Debugging

### Logs
- Service logs are in `logs/`
- MongoDB logs in `data/db/mongod.log`
- Access logs via Docker:
  ```bash
  docker-compose logs -f [service_name]
  ```

### Metrics
- Prometheus metrics at `:50055/metrics`
- MongoDB metrics via MongoDB Compass
- Service health checks at `/health` endpoints

### Common Issues
1. **MongoDB Connection**
   ```bash
   # Check MongoDB status
   docker-compose ps mongo
   # View MongoDB logs
   docker-compose logs mongo
   ```

2. **Service Communication**
   ```bash
   # Test gRPC connectivity
   grpcurl -plaintext localhost:50051 list
   ```

3. **Environment Issues**
   ```bash
   # Verify environment
   python -c "import os; print(os.getenv('MONGO_URI'))"
   ```

## API Documentation

### gRPC Services
- Service definitions in `protos/`
- Generated stubs in `src/interviewers/generated/`
- Example usage in `examples/`

### HTTP Endpoints
- OpenAPI documentation at `/docs`
- Swagger UI at `/swagger`

## License
[Add License Information]

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.
