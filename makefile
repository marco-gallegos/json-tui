.PHONY: changelog doctor

changelog:
	git cliff --output CHANGELOG.md

bump-minor:
	uv version --bump minor
	git tag "v$$(uv version --short)"
	$(MAKE) changelog
	git add .

bump-patch:
	uv version --bump patch
	git add pyproject.toml uv.lock
	git commit -m "chore: v$$(uv version --short)"
	git tag "v$$(uv version --short)"

doctor:
	@printf "Checking project requirements...\n"
	@command -v uv >/dev/null 2>&1 && printf "  [OK]   uv: %s\n" "$$(uv --version)" || { printf "  [MISS] uv is not installed\n"; }
	@command -v git-cliff >/dev/null 2>&1 && printf "  [OK]   git-cliff: %s\n" "$$(git-cliff --version)" || { printf "  [MISS] git-cliff is not installed\n"; }


