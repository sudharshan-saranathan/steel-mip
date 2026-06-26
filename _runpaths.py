"""Shared output paths, organised per run: runs/<RUN>/{plots,csv}.
RUN defaults to ET1.8; override with the RUN env var."""
import os
_PROJECT = os.path.dirname(os.path.abspath(__file__))
RUN   = os.environ.get("RUN", "ET1.8")
PLOTS = os.path.join(_PROJECT, "runs", RUN, "plots")
CSV   = os.path.join(_PROJECT, "runs", RUN, "csv")
os.makedirs(PLOTS, exist_ok=True)
os.makedirs(CSV, exist_ok=True)
