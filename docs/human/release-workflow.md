# Release Workflow

Swarm v3.2+ uses a semi-automated release process driven by the `orchestrator.py` CLI. this ensures strict version control and meaningful changelogs.

## Prerequisites
- No uncommitted changes in your working directory.
- `pyproject.toml` and `CHANGELOG.md` present in root.

## Workflow

### 1. Run the Release Command
Use the `release` command to handle version bumping and changelog updates.

```bash
# For a patch release (e.g., 3.2.0 -> 3.2.1)
python orchestrator.py release patch

# For a minor release (e.g., 3.2.0 -> 3.3.0)
python orchestrator.py release minor
```

**What this does:**
1.  **Bumps Version**: Updates `version` in `pyproject.toml`.
2.  **Updates Changelog**: Moves the `[Unreleased]` section to `[vX.Y.Z] - YYYY-MM-DD` in `CHANGELOG.md`.
3.  **Instruction**: Prints the git commands needed to finalize the release.

### 2. Finalize Git State
The command will output the exact git steps, typically:

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore(release): prepare v3.3.0"
git tag v3.3.0
git push origin main --tags
```

### 3. GitHub Actions
Pushing the tag (`v*`) triggers the **Release Management** workflow (`.github/workflows/release.yml`), which:
1.  Drafts a GitHub Release.
2.  Compiles release notes from `CHANGELOG.md`.
3.  Builds and publishes Docker images (via `docker-publish.yml`).

## Versioning Policy
We follow [Semantic Versioning](https://semver.org/):
- **Major**: Breaking changes (API changes, removal of deprecated features).
- **Minor**: New features, backwards compatible.
- **Patch**: Bug fixes, documentation updates.
