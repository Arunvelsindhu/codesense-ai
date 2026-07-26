import subprocess

def run_python_test_in_sandbox(test_code: str) -> dict:
    """
    Placeholder for running generated unit tests safely.
    For now runs locally; can be upgraded to actual Docker sandboxing later.
    """
    try:
        with open("temp_test.py", "w", encoding="utf-8") as f:
            f.write(test_code)

        result = subprocess.run(
            ["python", "-m", "pytest", "temp_test.py", "-v"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        return {
            "passed": result.returncode == 0,
            "output": result.stdout + result.stderr,
        }
    except Exception as e:
        return {"passed": False, "output": str(e)}