"""
KrishiSaathi (कृषि साथी) — Production Application Entry Point & CLI
"""
import sys
import argparse
import uvicorn
from app.config import APP_HOST, APP_PORT, APP_RELOAD

def run_server(host=None, port=None, reload=None):
    """Starts the FastAPI production server."""
    h = host or APP_HOST
    p = port or APP_PORT
    r = reload if reload is not None else APP_RELOAD
    print(f"Starting KrishiSaathi server on http://{h}:{p} (reload={r})...")
    uvicorn.run("app.main:app", host=h, port=p, reload=r)

def init_database():
    """Initializes and migrates database tables."""
    from app.db.session import init_db
    print("Initializing KrishiSaathi relational database...")
    init_db()
    print("Database tables initialized successfully.")

def run_eval():
    """Runs the AI evaluation benchmark against realistic Indian farmer queries."""
    import subprocess
    print("Running KrishiSaathi AI Evaluation Benchmark...")
    cmd = [sys.executable, "-m", "pytest", "-v", "tests/test_eval_benchmark.py"]
    ret = subprocess.run(cmd)
    sys.exit(ret.returncode)

def main():
    parser = argparse.ArgumentParser(
        description="KrishiSaathi (कृषि साथी) — Multimodal AI Agricultural Advisory System"
    )
    parser.add_argument(
        "action",
        nargs="?",
        default="run",
        choices=["run", "init-db", "eval"],
        help="Action to perform: run server, initialize database, or run evaluation benchmark"
    )
    parser.add_argument("--host", default=None, help="Host address to bind server")
    parser.add_argument("--port", type=int, default=None, help="Port to bind server")
    parser.add_argument("--reload", action="store_true", default=None, help="Enable auto-reload")
    args = parser.parse_args()

    if args.action == "run":
        run_server(host=args.host, port=args.port, reload=args.reload)
    elif args.action == "init-db":
        init_database()
    elif args.action == "eval":
        run_eval()

if __name__ == "__main__":
    main()