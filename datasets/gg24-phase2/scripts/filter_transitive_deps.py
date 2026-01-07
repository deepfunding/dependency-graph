"""
Filter transitive dependencies from the seed repos dependency graph.

This script removes transitive dependencies from seedReposWithDependencies.json
using a list of identified transitive dependencies.

Background:
-----------
The transitive dependencies in seedReposWithTransitiveDependencies.json were
identified by an LLM-based agent that analyzed each (repo, dependency) pair.
For each dependency, the agent searched the repository's source code using
ripgrep to find actual usage (imports, function calls, etc.).

Dependencies that appeared only in lockfiles (Cargo.lock, package-lock.json,
go.sum, etc.) but not in manifest files (Cargo.toml, package.json, go.mod) or
source code were classified as transitive—meaning they were pulled in
indirectly as dependencies of direct dependencies.

The agent's classifications were validated through multiple revalidation passes
to reduce false negatives caused by LLM non-determinism, with the merged
results using "take-best" logic to keep the most accurate classification when
multiple analyses existed for the same dependency.

Input files:
- seedReposWithDependencies.json: Full dependency graph
- seedReposWithTransitiveDependencies.json: Dependencies to remove (transitive)

Output file:
- seedReposWithNoTransitiveDependencies.json: Filtered dependency graph
"""

import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent

INPUT_FILE = DATA_DIR / "seedReposWithDependencies.json"
TRANSITIVE_FILE = DATA_DIR / "seedReposWithTransitiveDependencies.json"
OUTPUT_FILE = DATA_DIR / "seedReposWithNoTransitiveDependencies.json"


def load_json(filepath: Path) -> dict:
    """Load JSON file and return parsed data."""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_json(data: dict, filepath: Path) -> None:
    """Save data to JSON file with pretty formatting."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def filter_transitive_dependencies(
    all_deps: dict[str, list[str]],
    transitive_deps: dict[str, list[str]]
) -> tuple[dict[str, list[str]], dict]:
    """
    Remove transitive dependencies from each seed repo's dependency list.

    Args:
        all_deps: Map of seed repo -> list of all dependencies
        transitive_deps: Map of seed repo -> list of transitive dependencies

    Returns:
        Tuple of (filtered_deps, stats) where stats contains per-repo counts
    """
    filtered_deps = {}
    stats = {}

    for seed_repo, dependencies in all_deps.items():
        before_count = len(dependencies)

        # Get transitive deps for this seed repo (empty list if not present)
        to_remove = set(transitive_deps.get(seed_repo, []))

        # Filter out transitive dependencies
        direct_deps = [dep for dep in dependencies if dep not in to_remove]

        after_count = len(direct_deps)
        removed_count = before_count - after_count

        filtered_deps[seed_repo] = sorted(direct_deps)
        stats[seed_repo] = {
            'before': before_count,
            'after': after_count,
            'removed': removed_count
        }

    return filtered_deps, stats


def main():
    """Main execution function."""
    print(f"Loading dependencies from {INPUT_FILE}...")
    all_deps = load_json(INPUT_FILE)

    print(f"Loading transitive dependencies from {TRANSITIVE_FILE}...")
    transitive_deps = load_json(TRANSITIVE_FILE)

    print(f"Filtering transitive dependencies...")
    filtered_deps, stats = filter_transitive_dependencies(all_deps, transitive_deps)

    # Sort output alphabetically by seed repo
    filtered_deps_sorted = dict(sorted(filtered_deps.items()))

    # Print per-repo stats
    print(f"\nPer-repo statistics:")
    for seed_repo in sorted(stats.keys()):
        s = stats[seed_repo]
        print(f"  {seed_repo}: {s['before']} -> {s['after']} (-{s['removed']} transitive)")

    # Save filtered data
    print(f"\nSaving filtered data to {OUTPUT_FILE}...")
    save_json(filtered_deps_sorted, OUTPUT_FILE)

    # Print summary
    total_before = sum(s['before'] for s in stats.values())
    total_after = sum(s['after'] for s in stats.values())
    total_removed = sum(s['removed'] for s in stats.values())

    print(f"\nSummary:")
    print(f"  Seed repos processed: {len(stats)}")
    print(f"  Total dependencies before: {total_before}")
    print(f"  Total dependencies after: {total_after}")
    print(f"  Transitive dependencies removed: {total_removed}")


if __name__ == "__main__":
    main()
