"""
Run the bank API on http://127.0.0.1:5001 to explore it by hand (Postman, curl).

    python run_server.py               # latest release (1.2)
    python run_server.py 1.1           # the release with regressions

The automated tests do NOT need this: they start their own server.
"""
import sys

from app.bank_app import RELEASES, create_app

if __name__ == "__main__":
    release = sys.argv[1] if len(sys.argv) > 1 else "1.2"
    if release not in RELEASES:
        sys.exit(f"Unknown release {release}. Choose from: {', '.join(RELEASES)}")
    print(f"Starting bank API release {release} on http://127.0.0.1:5001")
    create_app(release).run(host="127.0.0.1", port=5001)
