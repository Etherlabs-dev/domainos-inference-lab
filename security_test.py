"""Guarded security check; importing does not contact Modal."""
from lab_cli import run_cloud

if __name__ == "__main__":
    raise SystemExit(run_cloud("security"))
