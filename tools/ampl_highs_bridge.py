"""Solve the steel model with HiGHS when only an AMPL demo licence is present.

The AMPL demo refuses to solve or write problems larger than 2,000 variables,
but `expand` still prints every constraint with its numeric coefficients. This
bridge:

  1. builds the model in AMPL exactly as the study drivers do,
  2. reads the expanded LP (objective + constraints) and the variable bounds,
  3. solves it with HiGHS (highspy),
  4. writes the primal solution back into AMPL with `let`, so post-solve
     report files (e.g. structural/report.mod) run unchanged.

With a full AMPL licence, use `option solver highs; solve;` instead; the bridge
exists only to make the audit reproducible without one.

Usage (from the model repository root):
    from ampl_highs_bridge import solve_bridge
    ampl = AMPL(); ampl.cd(ROOT); ampl.eval("include core/model.mod; ...")
    status, obj = solve_bridge(ampl)
"""
import os
import re
import tempfile

import highspy
import numpy as np

_TERM = re.compile(r"([+-]?)\s*(?:(\d[\d.eE+-]*)\s*\*\s*)?([A-Za-z_]\w*(?:\[[^\]]*\])?)")
_NUM = r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?|[+-]?Infinity"


def _parse_linear(expr):
    """Return {varname: coef} for a linear AMPL expression (no constants)."""
    coefs = {}
    s = expr.replace("\n", " ").replace("\t", " ").strip()
    pos = 0
    while pos < len(s):
        m = _TERM.match(s, pos)
        if not m or m.end() == pos:
            if s[pos] == " ":
                pos += 1
                continue
            raise ValueError(f"cannot parse near: {s[pos:pos+60]!r}")
        sign = -1.0 if m.group(1) == "-" else 1.0
        coef = float(m.group(2)) if m.group(2) else 1.0
        name = m.group(3).replace(" ", "")
        coefs[name] = coefs.get(name, 0.0) + sign * coef
        pos = m.end()
        while pos < len(s) and s[pos] == " ":
            pos += 1
    return coefs


def _num(x):
    x = x.strip()
    if x in ("Infinity", "+Infinity"):
        return np.inf
    if x == "-Infinity":
        return -np.inf
    return float(x)


def _read_expand(path):
    """Parse AMPL `expand` output into objective and constraint rows."""
    text = open(path).read()
    blocks = [b.strip() for b in re.split(r";\s*\n", text) if b.strip()]
    obj, rows = None, []
    for b in blocks:
        head, _, body = b.partition(":")
        head = head.strip()
        if head.startswith(("minimize", "maximize")):
            sense = head.split()[0]
            obj = (sense, _parse_linear(body))
            continue
        if not head.startswith("subject to"):
            raise ValueError(f"unexpected block: {b[:80]!r}")
        name = head[len("subject to"):].strip()
        body = body.strip().rstrip(";")
        # forms: expr = c | expr <= c | expr >= c | c1 <= expr <= c2
        m = re.fullmatch(rf"\s*({_NUM})\s*<=\s*(.*?)\s*<=\s*({_NUM})\s*", body, re.S)
        if m:
            rows.append((name, _parse_linear(m.group(2)), _num(m.group(1)), _num(m.group(3))))
            continue
        m = re.fullmatch(rf"(.*?)\s*(<=|>=|=)\s*({_NUM})\s*", body, re.S)
        if not m:
            raise ValueError(f"cannot parse constraint {name}: {body[:120]!r}")
        lhs, op, rhs = m.group(1), m.group(2), _num(m.group(3))
        lo, hi = {"=": (rhs, rhs), "<=": (-np.inf, rhs), ">=": (rhs, np.inf)}[op]
        rows.append((name, _parse_linear(lhs), lo, hi))
    return obj, rows


def _key(vname, idx):
    if idx is None or idx == ():
        return vname
    idx = idx if isinstance(idx, tuple) else (idx,)
    return f"{vname}[{','.join(str(int(i)) if isinstance(i, float) and float(i).is_integer() else str(i) for i in idx)}]"


def _var_bounds(ampl):
    """Variable bounds from the declarations (the demo blocks var.lb/var.ub).

    Each bound expression is evaluated through a temporary AMPL param with
    the variable's own indexing, so bounds such as `<= dem[t]` are exact.
    """
    bounds = {}
    for k, (vname, _) in enumerate(ampl.get_variables()):
        decl = " ".join(ampl.get_output(f"show {vname};").split())
        m = re.match(rf"var {re.escape(vname)}\s*(\{{[^}}]*\}})?\s*(.*?);?$", decl)
        idxset, attrs = (m.group(1) or ""), m.group(2)
        found = {}
        for op, expr in re.findall(r"(>=|<=|:=|=)\s*([^,]+)", attrs):
            found[op] = expr.strip().rstrip(";")
        vals = {}
        for op in (">=", "<="):
            if op not in found:
                continue
            p = f"__bnd{k}_{'lo' if op == '>=' else 'hi'}"
            ampl.eval(f"param {p}{idxset} := {found[op]};")
            par = ampl.get_parameter(p)
            if idxset:
                vals[op] = {_key(vname, i): v for i, v in par.get_values().to_dict().items()}
            else:
                vals[op] = {vname: par.value()}
        for idx, _ in ampl.get_variable(vname).instances():
            key = _key(vname, idx)
            lo = vals[">="].get(key, -np.inf) if ">=" in vals else -np.inf
            hi = vals["<="].get(key, np.inf) if "<=" in vals else np.inf
            bounds[key] = (lo, hi)
    return bounds


def solve_bridge(ampl, tol=1e-7, verbose=False):
    """Expand, solve with HiGHS, load the solution back. Returns (status, obj)."""
    tmp = tempfile.mkdtemp(prefix="bridge_")
    path = os.path.join(tmp, "expand.txt")
    ampl.eval("option expand_precision 0;")
    ampl.eval(f'expand > "{path}";')
    ampl.eval(f'close "{path}";')
    (sense, objc), rows = _read_expand(path)
    bounds = _var_bounds(ampl)

    names = sorted(set(bounds) | set(objc) | {v for _, c, _, _ in rows for v in c})
    col = {n: i for i, n in enumerate(names)}
    h = highspy.Highs()
    h.setOptionValue("output_flag", verbose)
    h.setOptionValue("primal_feasibility_tolerance", tol)
    h.setOptionValue("dual_feasibility_tolerance", tol)
    inf = highspy.kHighsInf
    for n in names:
        lb, ub = bounds.get(n, (0.0, np.inf))
        lb = -inf if lb is None or lb <= -1e20 else lb
        ub = inf if ub is None or ub >= 1e20 else ub
        h.addVar(lb, ub)
    cost = np.zeros(len(names))
    for n, c in objc.items():
        cost[col[n]] = c
    h.changeColsCost(len(names), np.arange(len(names), dtype=np.int32), cost)
    h.changeObjectiveSense(highspy.ObjSense.kMinimize if sense == "minimize"
                           else highspy.ObjSense.kMaximize)
    for _, coefs, lo, hi in rows:
        idx = np.array([col[v] for v in coefs], dtype=np.int32)
        val = np.array(list(coefs.values()), dtype=float)
        h.addRow(-inf if lo == -np.inf else lo, inf if hi == np.inf else hi,
                 len(idx), idx, val)
    h.run()
    status = h.modelStatusToString(h.getModelStatus())
    if h.getModelStatus() != highspy.HighsModelStatus.kOptimal:
        return status, None
    x = h.getSolution().col_value
    # write solution back into AMPL (current values of variables)
    by_var = {}
    for n, i in col.items():
        base, _, rest = n.partition("[")
        by_var.setdefault(base, []).append((rest.rstrip("]"), x[i]))
    for base, items in by_var.items():
        stmts = []
        for idx, v in items:
            ref = f"{base}[{idx}]" if idx else base
            stmts.append(f"let {ref} := {v!r};")
        for k in range(0, len(stmts), 500):
            ampl.eval("\n".join(stmts[k:k + 500]))
    return "solved", h.getInfo().objective_function_value
