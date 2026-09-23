# Collapse the current branch to one root commit and push it to origin.
# Preserve .git. Only move the local branch after the guarded push succeeds.

.DEFAULT_GOAL := help
.PHONY: help budget init

help:
	@echo "make budget - Zeigt das verbleibende Coding-Budget in Prozent."
	@echo "make init  - Squash the current branch into one 'init' commit and push to origin."

budget:
	@clear 2>/dev/null || true
	@python .devcontainer/pi.py --budget

init:
	@set -eu; \
	branch=$$(git symbolic-ref -q HEAD) || { echo 'Switch to a branch first.' >&2; exit 1; }; \
	name=$${branch#refs/heads/}; \
	for state in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD rebase-merge rebase-apply sequencer; do \
		if [ -e "$$(git rev-parse --git-path "$$state")" ]; then \
			echo 'Finish or abort the current Git operation first.' >&2; exit 1; \
		fi; \
	done; \
	git remote get-url origin >/dev/null; \
	previous=$$(git rev-parse --verify HEAD 2>/dev/null || true); \
	git fetch --no-tags --prune origin; \
	expected=$$(git rev-parse --verify "refs/remotes/origin/$$name" 2>/dev/null || true); \
	if [ -n "$$expected" ] && ! git merge-base --is-ancestor "$$expected" "$${previous:-HEAD}"; then \
		echo 'Remote has changes missing locally. Integrate them before running make init.' >&2; exit 1; \
	fi; \
	git add -A; \
	tree=$$(git write-tree); \
	commit=$$(printf 'init\n' | git commit-tree "$$tree"); \
	git push --force-with-lease="$$branch:$$expected" origin "$$commit:$$branch"; \
	git update-ref -m 'make init' "$$branch" "$$commit" "$$previous"; \
	git branch --set-upstream-to="origin/$$name" "$$name" >/dev/null; \
	git log -1 --oneline
