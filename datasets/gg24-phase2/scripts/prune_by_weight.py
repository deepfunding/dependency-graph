"""
Prune dependencies by weight for repos exceeding the dependency limit.

This script takes seedReposWithNoTransitiveDependencies.json and caps repos
with >70 dependencies by keeping only the top 70 weighted dependencies.

Repos with ≤70 dependencies are kept unchanged.

Input files:
- seedReposWithNoTransitiveDependencies.json: Dependency graph with transitive deps removed
- seedReposWithDependencyWeights.json: Weights for dependencies in repos exceeding 70 deps

Output file:
- seedReposWithNoTransitiveDependenciesWeightPruned.json: Capped to max 70 deps per repo
"""

import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent

MAX_DEPS = 70

INPUT_FILE = DATA_DIR / "seedReposWithNoTransitiveDependencies.json"
WEIGHTS_FILE = DATA_DIR / "seedReposWithDependencyWeights.json"
OUTPUT_FILE = DATA_DIR / "seedReposWithNoTransitiveDependenciesWeightPruned.json"


def load_json(filepath: Path) -> dict:
    """Load JSON file and return parsed data."""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_json(data: dict, filepath: Path) -> None:
    """Save data to JSON file with pretty formatting."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def prune_by_weight(
    all_deps: dict[str, list[str]],
    weights: dict[str, dict[str, float]],
    max_deps: int
) -> tuple[dict[str, list[str]], dict]:
    """
    Prune repos with >max_deps dependencies by keeping top weighted ones.

    Args:
        all_deps: Map of seed repo -> list of dependencies
        weights: Map of seed repo -> {dependency: weight} for repos needing pruning
        max_deps: Maximum number of dependencies to keep per repo

    Returns:
        Tuple of (pruned_deps, stats) where stats contains per-repo counts
    """
    pruned_deps = {}
    stats = {}

    for seed_repo, dependencies in all_deps.items():
        before_count = len(dependencies)

        if before_count <= max_deps:
            # Keep unchanged
            pruned_deps[seed_repo] = sorted(dependencies)
            stats[seed_repo] = {
                'before': before_count,
                'after': before_count,
                'pruned': False
            }
        else:
            # Need to prune - use weights
            repo_weights = weights.get(seed_repo, {})

            # Sort dependencies by weight (descending), keep top max_deps
            # Dependencies not in weights get weight 0
            deps_with_weights = [
                (dep, repo_weights.get(dep, 0.0))
                for dep in dependencies
            ]
            deps_with_weights.sort(key=lambda x: x[1], reverse=True)

            top_deps = [dep for dep, _ in deps_with_weights[:max_deps]]
            after_count = len(top_deps)

            pruned_deps[seed_repo] = sorted(top_deps)
            stats[seed_repo] = {
                'before': before_count,
                'after': after_count,
                'pruned': True
            }

    return pruned_deps, stats


def main():
    """Main execution function."""
    print(f"Loading dependencies from {INPUT_FILE}...")
    all_deps = load_json(INPUT_FILE)

    print(f"Loading weights from {WEIGHTS_FILE}...")
    weights = load_json(WEIGHTS_FILE)

    print(f"Pruning repos with >{MAX_DEPS} dependencies...")
    pruned_deps, stats = prune_by_weight(all_deps, weights, MAX_DEPS)

    # Sort output alphabetically by seed repo
    pruned_deps_sorted = dict(sorted(pruned_deps.items()))

    # Print stats for pruned repos only
    pruned_repos = [repo for repo, s in stats.items() if s['pruned']]
    print(f"\nRepos pruned ({len(pruned_repos)}):")
    for seed_repo in sorted(pruned_repos):
        s = stats[seed_repo]
        print(f"  {seed_repo}: {s['before']} -> {s['after']}")

    # Save pruned data
    print(f"\nSaving to {OUTPUT_FILE}...")
    save_json(pruned_deps_sorted, OUTPUT_FILE)

    # Print summary
    total_before = sum(s['before'] for s in stats.values())
    total_after = sum(s['after'] for s in stats.values())

    print(f"\nSummary:")
    print(f"  Seed repos: {len(stats)}")
    print(f"  Repos pruned: {len(pruned_repos)}")
    print(f"  Total dependencies before: {total_before}")
    print(f"  Total dependencies after: {total_after}")
    print(f"  Dependencies removed: {total_before - total_after}")


if __name__ == "__main__":
    main()
