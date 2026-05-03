#!/usr/bin/env python3
"""Git push over SSH using asyncssh.

Usage: python3 ssh_push.py /path/to/repo [branch]
"""

import asyncio
import asyncssh
import subprocess
import sys
import os


async def push(repo_path: str, branch: str = "main"):
    key_path = os.path.expanduser("~/.ssh/id_rsa_buildcore")
    
    if not os.path.exists(key_path):
        print(f"SSH key not found: {key_path}")
        sys.exit(1)
    
    # Get remote info
    result = subprocess.run(
        ["git", "-C", repo_path, "remote", "get-url", "origin"],
        capture_output=True, text=True
    )
    remote_url = result.stdout.strip()
    
    # Parse: git@github.com:user/repo.git
    if remote_url.startswith("git@"):
        host_path = remote_url[4:]  # github.com:user/repo.git
        host, repo_git = host_path.split(":", 1)
        repo = repo_git.replace(".git", "")
    else:
        print(f"Unsupported remote URL: {remote_url}")
        sys.exit(1)
    
    print(f"Pushing to {host}:{repo} (branch: {branch})...")
    
    try:
        conn = await asyncio.wait_for(
            asyncssh.connect(
                host,
                username="git",
                client_keys=[key_path],
                known_hosts=None,
            ),
            timeout=15
        )
        
        # Use git's upload-pack/receive-pack over SSH
        # We'll pipe git's output through the SSH connection
        proc = await conn.create_process(
            f"git-receive-pack '{repo}.git'",
            encoding=None,
        )
        
        # Run git send-pack locally
        local_proc = subprocess.Popen(
            ["git", "-C", repo_path, "send-pack", f"ssh://{host}/{repo}.git", branch],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        # This simple approach won't work due to protocol complexity
        # We need to use GIT_SSH_COMMAND or implement the full protocol
        
        conn.close()
        
    except asyncssh.PermissionDenied:
        print("ERROR: Permission denied - SSH key not authorized on GitHub")
        print("Add this public key as a deploy key in your GitHub repo settings:")
        key = asyncssh.read_private_key(key_path)
        pub = key.export_public_key()
        print(pub.decode() if isinstance(pub, bytes) else pub)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    branch = sys.argv[2] if len(sys.argv) > 2 else "main"
    asyncio.run(push(repo, branch))
