# Contributing to OpenSkill Studio

Thank you for your interest in contributing! 🎉

## Development Setup

See [README.md](README.md) for local setup instructions.

## Code Style

- **Frontend**: ESLint + Prettier (auto-fixed on commit via husky)
- **Backend**: Ruff (auto-fixed on commit)
- **Editor**: Use the recommended VS Code extensions (`.vscode/extensions.json`)

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation only
- `chore:` — maintenance / tooling
- `refactor:` — code change that neither fixes a bug nor adds a feature
- `test:` — adding or updating tests

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `feature/your-feature`
3. Make your changes
4. Run `make lint` and `make test`
5. Open a PR against `main`
6. All CI checks must pass
7. 1 reviewer approval required
8. PRs are squash-merged

## Issue Reporting

Use the GitHub Issue templates:

- **Bug Report** — for bugs and regressions
- **Feature Request** — for new functionality

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).
