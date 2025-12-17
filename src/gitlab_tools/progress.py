"""
Progress tracking and error reporting module.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from tqdm import tqdm


@dataclass
class ErrorRecord:
    """Record of an error that occurred during processing."""
    repository: str
    branch: str
    message: str


class ProgressManager:
    """Manages progress display and error tracking."""
    
    def __init__(self, total_repos: int, quiet: bool = False):
        """
        Initialize progress manager.
        
        Args:
            total_repos: Total number of repositories to process
            quiet: If True, suppress progress bar (for quiet mode)
        """
        self.total_repos = total_repos
        self.quiet = quiet
        self.processed = 0
        self.errors: List[ErrorRecord] = []
        self.progress_bar = None
        
        if total_repos > 0 and not quiet:
            self.progress_bar = tqdm(
                total=total_repos,
                desc="Processing repositories",
                unit="repo",
                ncols=80,
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{percentage:.0f}%]'
            )
    
    def update(self, count: int = 1):
        """
        Update progress bar.
        
        Args:
            count: Number of items to increment by
        """
        self.processed += count
        if self.progress_bar and not self.quiet:
            self.progress_bar.update(count)
    
    def record_error(self, repository: str, branch: str = "", message: str = ""):
        """
        Record an error that occurred.
        
        Args:
            repository: Name of repository where error occurred
            branch: Branch name (if applicable)
            message: Error message
        """
        self.errors.append(ErrorRecord(repository, branch, message))
    
    def close(self):
        """Close the progress bar."""
        if self.progress_bar:
            self.progress_bar.close()
    
    def print_summary(self):
        """Print summary of results including any errors."""
        print("\n" + "=" * 80)
        print(f"PROCESSING COMPLETE: {self.processed}/{self.total_repos} repositories processed")
        print("=" * 80)
        
        if not self.errors:
            print("\n✓ No errors encountered!")
        else:
            print(f"\n✗ {len(self.errors)} ERROR(S) ENCOUNTERED:\n")
            
            # Group errors by repository
            errors_by_repo: Dict[str, List[ErrorRecord]] = {}
            for error in self.errors:
                if error.repository not in errors_by_repo:
                    errors_by_repo[error.repository] = []
                errors_by_repo[error.repository].append(error)
            
            # Print errors grouped by repository
            for repo_name in sorted(errors_by_repo.keys()):
                print(f"Repository: {repo_name}")
                for error in errors_by_repo[repo_name]:
                    if error.branch:
                        print(f"  • Branch [{error.branch}]: {error.message}")
                    else:
                        print(f"  • {error.message}")
                print()


class BranchProgressManager:
    """Manages progress for branch operations within a repository."""
    
    def __init__(self, repo_name: str, total_branches: int, quiet: bool = False):
        """
        Initialize branch progress manager.
        
        Args:
            repo_name: Name of repository
            total_branches: Total number of branches
            quiet: If True, suppress progress bar
        """
        self.repo_name = repo_name
        self.total_branches = total_branches
        self.quiet = quiet
        self.errors: List[Tuple[str, str]] = []  # (branch_name, error_message)
        self.progress_bar = None
        
        if total_branches > 0 and not quiet:
            self.progress_bar = tqdm(
                total=total_branches,
                desc=f"  {repo_name}: branches",
                unit="branch",
                ncols=70,
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}',
                leave=False
            )
    
    def update(self, count: int = 1):
        """Update progress."""
        if self.progress_bar and not self.quiet:
            self.progress_bar.update(count)
    
    def record_error(self, branch: str, message: str):
        """Record branch error."""
        self.errors.append((branch, message))
    
    def close(self):
        """Close progress bar."""
        if self.progress_bar:
            self.progress_bar.close()
    
    def get_errors(self) -> List[ErrorRecord]:
        """Get errors as ErrorRecord objects."""
        return [
            ErrorRecord(self.repo_name, branch, message)
            for branch, message in self.errors
        ]
