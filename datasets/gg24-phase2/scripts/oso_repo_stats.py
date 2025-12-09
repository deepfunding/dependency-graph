import os
import json
from pathlib import Path
from dotenv import load_dotenv
from pyoso import Client

load_dotenv()
oso = Client(api_key=os.getenv("OSO_API_KEY"))

# Configuration
TOP_N = 100
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent
INPUT_FILE = DATA_DIR / "seedReposWithDependencies.json"
OUTPUT_FILE = DATA_DIR / "seedReposWithDependencies_pruned.json"


def stringify(arr):
    """Convert array to SQL string format."""
    return "'" + "','".join(arr) + "'"


def load_dependencies():
    """Load seed repos and their dependencies from JSON file."""
    with open(INPUT_FILE, 'r') as f:
        return json.load(f)


def get_ordered_dependencies(all_dependencies):
    """Query OSO to get dependencies ordered by priority."""
    query = f"""
    WITH opendevdata AS (
      SELECT
        repo_url,
        max(repo_created_at) AS repo_created_at,
        max(star_count) AS star_count,
        max(fork_count) AS fork_count,
        max(CASE WHEN ecosystem_id=2 THEN true ELSE false END) AS is_ethereum
      FROM (
        SELECT
          lower(r.link) AS repo_url,
          r.repo_created_at,
          r.num_stars AS star_count,
          r.num_forks AS fork_count,
          er.ecosystem_id
        FROM oso.stg_opendevdata__repos r
        JOIN oso.stg_opendevdata__ecosystems_repos_recursive er
          ON r.id=er.repo_id
      )
      GROUP BY repo_url
    ),
    oso_data AS (
      SELECT
        lower(artifact_url) AS repo_url,
        created_at AS repo_created_at,
        star_count,
        fork_count
      FROM repositories_v0
    ),
    repo_list AS (
      SELECT repo_url
      FROM UNNEST(ARRAY[{stringify(all_dependencies)}]) AS t(repo_url)
    )
    SELECT
      rl.repo_url,
      coalesce(od.repo_created_at,os.repo_created_at) AS repo_created_at,
      coalesce(od.star_count,os.star_count) AS star_count,
      coalesce(od.fork_count,os.fork_count) AS fork_count,
      coalesce(od.is_ethereum,false) AS is_ethereum
    FROM repo_list rl
    LEFT JOIN opendevdata od
      ON rl.repo_url=od.repo_url
    LEFT JOIN oso_data os
      ON rl.repo_url=os.repo_url
    ORDER BY
      is_ethereum DESC,
      fork_count DESC,
      star_count DESC,
      repo_created_at DESC
    """
    df = oso.to_pandas(query)
    return df['repo_url'].tolist()


def prune_dependencies(seed_repos_data, ordered_deps):
    """Prune dependencies for each seed repo to TOP_N based on order."""
    # Create a lookup for order (lower index = higher priority)
    dep_order = {repo: idx for idx, repo in enumerate(ordered_deps)}
    
    pruned_data = {}
    repo_stats = {}
    for seed_repo, dependencies in seed_repos_data.items():
        before_count = len(dependencies)
        
        # Filter to only dependencies that exist in ordered list
        # Sort by their order in the ordered_deps list
        valid_deps = [
            dep for dep in dependencies 
            if dep in dep_order
        ]
        valid_deps.sort(key=lambda x: dep_order[x])
        
        # Take TOP_N
        pruned_deps = valid_deps[:TOP_N]
        after_count = len(pruned_deps)
        
        pruned_data[seed_repo] = pruned_deps
        repo_stats[seed_repo] = {
            'before': before_count,
            'after': after_count
        }
    
    return pruned_data, repo_stats


def main():
    """Main execution function."""
    print(f"Loading dependencies from {INPUT_FILE}...")
    seed_repos_data = load_dependencies()
    
    # Collect all unique dependencies
    all_dependencies = set()
    for dependencies in seed_repos_data.values():
        all_dependencies.update(dependencies)
    all_dependencies = list(all_dependencies)
    
    print(f"Found {len(seed_repos_data)} seed repos with {len(all_dependencies)} unique dependencies")
    print(f"Querying OSO for dependency stats...")
    
    # Get ordered list of dependencies from OSO query
    ordered_deps = get_ordered_dependencies(all_dependencies)
    
    print(f"Pruning dependencies to top {TOP_N} per seed repo...")
    pruned_data, repo_stats = prune_dependencies(seed_repos_data, ordered_deps)
    
    # Print per-repo stats
    print(f"\nPer-repo statistics:")
    for seed_repo in sorted(repo_stats.keys()):
        stats = repo_stats[seed_repo]
        print(f"  {seed_repo}: {stats['before']} -> {stats['after']} dependencies")
    
    # Sort pruned data alphabetically by seed repo key
    pruned_data_sorted = dict(sorted(pruned_data.items()))
    
    # Save pruned data
    print(f"\nSaving pruned data to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(pruned_data_sorted, f, indent=2)
    
    # Print summary
    total_deps_before = sum(len(deps) for deps in seed_repos_data.values())
    total_deps_after = sum(len(deps) for deps in pruned_data.values())
    print(f"\nSummary:")
    print(f"  Total dependencies before: {total_deps_before}")
    print(f"  Total dependencies after: {total_deps_after}")
    print(f"  Reduction: {total_deps_before - total_deps_after} dependencies removed")


if __name__ == "__main__":
    main()
