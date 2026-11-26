#!/usr/bin/env python3
"""Cross-check the API routes matrix in docs/2_design.md against docs/api/openapi.yaml.

Every "METHOD URI" pair from the OpenAPI specification must appear exactly once
in the matrix (rows starting with "| API-"), and the matrix must not contain
routes that are absent from the specification.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
spec = yaml.safe_load((ROOT / "docs/api/openapi.yaml").read_text(encoding="utf-8"))
design = (ROOT / "docs/2_design.md").read_text(encoding="utf-8")

methods = {"get", "post", "put", "patch", "delete"}
spec_routes = {
    f"{m.upper()} {path}"
    for path, ops in spec["paths"].items()
    for m in ops
    if m in methods
}

row = re.compile(r"^\| API-\d+ \| (GET|POST|PUT|PATCH|DELETE) \| `([^`]+)` \|", re.M)
matrix = [f"{m} {u}" for m, u in row.findall(design)]
matrix_routes = set(matrix)

missing = sorted(spec_routes - matrix_routes)
extra = sorted(matrix_routes - spec_routes)
dupes = sorted({r for r in matrix if matrix.count(r) > 1})

for title, items in (("Missing in matrix", missing), ("Not in OpenAPI", extra), ("Duplicated", dupes)):
    for item in items:
        print(f"{title}: {item}")

print(f"OpenAPI operations: {len(spec_routes)}, matrix rows: {len(matrix)}")
sys.exit(1 if missing or extra or dupes else 0)
