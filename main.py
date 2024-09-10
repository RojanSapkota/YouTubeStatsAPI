import os
from datetime import datetime, timedelta
import time

def remove_old_commits(last_good_commit_hash: str):
    """Remove commits after a specific commit hash."""
    os.system(f'git reset --hard {last_good_commit_hash}')
    os.system('git push origin main --force')

def make_commits_for_today(total_commits: int, commits_per_push: int = 1000, cooldown_seconds: int = 5):
    """Generate multiple commits for today with batching, file reset, and cooldown."""
    current_date = datetime.now()
    commit_batch = 0

    for i in range(total_commits):
        commit_time = current_date + timedelta(minutes=i*10)  # 10-minute intervals
        commit_date = commit_time.strftime('%Y-%m-%d %H:%M:%S')

        # Overwrite the file with a small update to avoid flooding
        with open('data.txt', 'w') as file:
            file.write(f'Temporary commit {i+1} made on {commit_date}\n')

        # Stage the file
        os.system('git add data.txt')

        # Commit with the specific commit date
        os.system(f'git commit --date="{commit_date}" -m "Commit {i+1} for {commit_time.strftime("%Y-%m-%d %H:%M:%S")}"')

        # Push every `commits_per_push` commits to avoid overwhelming GitHub
        if (i + 1) % commits_per_push == 0:
            commit_batch += 1
            print(f"Pushing batch {commit_batch} of {commits_per_push} commits.")
            os.system('git push')
            
            # Introduce cooldown to prevent hitting GitHub's rate limits
            print(f"Cooldown for {cooldown_seconds} seconds.")
            time.sleep(cooldown_seconds)

    # Final push for any remaining commits after the last batch
    if total_commits % commits_per_push != 0:
        print("Pushing remaining commits.")
        os.system('git push')

# Example usage
if __name__ == "__main__":
    # Last good commit hash before the new commits
    last_good_commit_hash = '1234abcd'  # Example commit hash

    # Remove old commits if needed
    remove_old_commits(last_good_commit_hash)

    # Generate a large number of commits for today (e.g., 2000 commits)
    make_commits_for_today(total_commits=3000, commits_per_push=1000, cooldown_seconds=10)
