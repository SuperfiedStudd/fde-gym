"""Reset local Docker data, then recreate and enqueue deterministic seed jobs."""

import subprocess
import sys
import time
import urllib.request


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def wait_for_api(timeout: int = 90) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen("http://localhost:8000/health", timeout=2) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(2)
    raise TimeoutError("API did not become healthy")


if __name__ == "__main__":
    run("docker", "compose", "down", "--volumes")
    run("docker", "compose", "up", "--detach", "postgres", "redis", "api", "worker", "edge-service")
    wait_for_api()
    run(sys.executable, "scripts/seed/enqueue.py")
    print("ClaimOps seed data reset complete")
