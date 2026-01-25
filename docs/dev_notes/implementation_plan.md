# Implementation Plan - Key Improvements

We will modernize the **Kitsune** project by improving dependency management, security, and CI/CD pipelines.

## User Review Required

> [!IMPORTANT]
> This plan involves **deleting `requirements.txt`** and switching to **Poetry** for dependency management. This changes how you install and run the project locally (e.g., `poetry install` instead of `pip install -r requirements.txt`).

## Proposed Changes

### 1. Dependency Management (Poetry)

Migrate from `requirements.txt` to `poetry`.

#### [MODIFY] [pyproject.toml](file:///home/medalcode/Documentos/GitHub/Kitsune/pyproject.toml)

- Add `[tool.poetry]` sections.
- Move dependencies from `requirements.txt` to `pyproject.toml`.
- Separate dev dependencies (`pytest`, `ruff`) from main dependencies.

#### [DELETE] [requirements.txt](file:///home/medalcode/Documentos/GitHub/Kitsune/requirements.txt)

#### [MODIFY] [README.md](file:///home/medalcode/Documentos/GitHub/Kitsune/README.md)

- Update installation instructions to use Poetry.

### 2. Docker Security & Optimization

Switch to a non-root user and optimize the build.

#### [MODIFY] [Dockerfile](file:///home/medalcode/Documentos/GitHub/Kitsune/Dockerfile)

- Create a dedicated `appuser`.
- Switch context to run as `appuser`.
- Update build steps to use Poetry for exporting requirements (or installing directly if preferred, but export is safer for slim images).

### 3. CI/CD Improvements

Update GitHub Actions to support the new workflow.

#### [MODIFY] [.github/workflows/ci.yml](file:///home/medalcode/Documentos/GitHub/Kitsune/.github/workflows/ci.yml)

- Install Poetry in the CI environment.
- Use `poetry install` for dependencies.
- Enable `pytest-cov` for coverage reports (optional but recommended).

## Verification Plan

### Automated Tests

- Run `poetry lock` and `poetry install` to verify dependency resolution.
- Run `poetry run pytest` to ensure tests pass with the new environment.
- Build the Docker image: `docker build -t kitsune .` and verify it runs.

### Manual Verification

- Check if the application starts locally: `poetry run uvicorn src.app.main:app --reload`
