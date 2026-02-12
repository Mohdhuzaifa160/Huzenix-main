import subprocess
import tempfile
import os

class CodeRunner:

    def run_python(self, code: str) -> str:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
                file_path = f.name
                f.write(code.encode())

            result = subprocess.run(
                ["python", file_path],
                capture_output=True,
                text=True,
                timeout=10
            )

            os.remove(file_path)

            if result.stderr:
                return f"Error:\n{result.stderr.strip()}"

            return result.stdout.strip() or "Code ran successfully with no output."

        except Exception as e:
            return f"Execution failed: {str(e)}"
