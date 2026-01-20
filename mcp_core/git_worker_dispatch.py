"""
Git Worker Dispatch Methods

Methods to dispatch specialized Git workers from orchestrator.
"""

from typing import Dict, Any
from mcp_core.swarm_schemas import Task
from mcp_core.worker_prompts import prompt_git_commit, prompt_git_pr, prompt_git_branch
import logging

logger = logging.getLogger(__name__)


def _dispatch_git_commit_worker(orchestrator, task: Task) -> Dict[str, Any]:
    """Dispatch the Commit Worker to create atomic commit."""
    git_context = {
        "output_files": task.output_files,
        "repo_owner": orchestrator.git.config.remote_url.split('/')[-2] if orchestrator.git.config.remote_url else None,
        "repo_name": orchestrator.git.config.remote_url.split('/')[-1].replace('.git', '') if orchestrator.git.config.remote_url else None,
    }
    
    prompt = prompt_git_commit(task, git_context)
    logger.info(f"Dispatching Commit Worker for task {task.task_id[:8]}")
    
    # In autonomous mode, this would call generate_response
    # For now, just log and return instructions
    return {
        "worker": "CommitWorker",
        "prompt": prompt,
        "status": "ready"
    }


def _dispatch_git_pr_worker(orchestrator, task: Task) -> Dict[str, Any]:
    """Dispatch the PR Worker to create pull request."""
    git_context = {
        "git_branch_name": task.git_branch_name or f"feature/task-{task.task_id[:8]}",
        "git_base_branch": task.git_base_branch,
        "git_pr_title": task.git_pr_title or task.description[:60],
        "git_pr_body": task.git_pr_body or f"Automated PR from Swarm task {task.task_id[:8]}",
        "output_files": task.output_files,
        "repo_owner": orchestrator.git.config.remote_url.split('/')[-2] if orchestrator.git.config.remote_url else None,
        "repo_name": orchestrator.git.config.remote_url.split('/')[-1].replace('.git', '') if orchestrator.git.config.remote_url else None,
    }
    
    prompt = prompt_git_pr(task, git_context)
    logger.info(f"Dispatching PR Worker for task {task.task_id[:8]}")
    
    return {
        "worker": "PRWorker",
        "prompt": prompt,
        "status": "ready"
    }


def _dispatch_git_branch_worker(orchestrator, task: Task) -> Dict[str, Any]:
    """Dispatch the Branch Worker to create feature branch."""
    git_context = {
        "git_branch_name": task.git_branch_name or f"feature/task-{task.task_id[:8]}",
        "git_base_branch": task.git_base_branch,
    }
    
    prompt = prompt_git_branch(task, git_context)
    logger.info(f"Dispatching Branch Worker for task {task.task_id[:8]}")
    
    return {
        "worker": "BranchWorker",
        "prompt": prompt,
        "status": "ready"
    }
