import json, time, os, hashlib, argparse, math

def T(x): return 0.8 * x
def R(Sigma, x): return 0.2 * (Sigma - x)
def Q(Sigma, x0): return -0.1 * (Sigma - x0)
def P(x): return max(min(x, 1.0), -1.0)

ap = argparse.ArgumentParser()
ap.add_argument("--lambda_c", type=float, required=True)
ap.add_argument("--alpha", type=float, required=True)
ap.add_argument("--rho", type=float, required=True)
ap.add_argument("--Umax", type=float, required=True)
ap.add_argument("--steps", type=int, required=True)
ap.add_argument("--x0", type=float, required=True)
ap.add_argument("--gamma", type=float, default=0.1)
ap.add_argument("--allow_kappa_ge_1", action="store_true")
args = ap.parse_args()

stamp = os.environ.get("RCCT_STAMP","run")
state_dir   = os.environ["RCCT_STATE_DIR"]
ledger_path = os.environ["RCCT_LEDGER_PATH"]

kappa = args.lambda_c + args.alpha
if (kappa >= 1.0) and (not args.allow_kappa_ge_1):
    raise SystemExit(f"RCCT GUARD: kappa=lambda+alpha={kappa:.4f} >= 1.0 (non-contractive). Use --allow_kappa_ge_1 to override.")

x = args.x0
x0 = x
Sigma = x

history = []
for _ in range(args.steps):
    u = args.rho * Q(Sigma, x0)
    if abs(u) > args.Umax:
        u = args.Umax * (1 if u > 0 else -1)

    x_new = P(T(x) + R(Sigma, x) + u)
    history.append(x_new)

    Sigma = (1.0 - args.gamma) * Sigma + args.gamma * x_new
    x = x_new

D = abs(x - x0)
Dsig = abs(Sigma - x0)
C = 1.0 - Dsig
S = C - D

R_max_est = 0.2 * abs(Sigma)
bound_radius = None
if kappa < 1.0:
    bound_radius = (R_max_est + args.Umax) / (1.0 - kappa)

out = {
  "stamp": stamp,
  "params": {
    "lambda_c": args.lambda_c,
    "alpha": args.alpha,
    "rho": args.rho,
    "Umax": args.Umax,
    "steps": args.steps,
    "x0": args.x0,
    "gamma": args.gamma
  },
  "kappa": kappa,
  "R_max_est": R_max_est,
  "bound_radius_est": bound_radius,
  "final_x": x,
  "Sigma": Sigma,
  "drift_D": D,
  "drift_DSigma": Dsig,
  "coherence_C": C,
  "stability_S": S,
  "history_tail": history[-10:]
}

os.makedirs(state_dir, exist_ok=True)
state_path = os.path.join(state_dir, f"rcct_state_{stamp}.json")
with open(state_path, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)

blob = json.dumps(out, sort_keys=True).encode("utf-8")
h = hashlib.sha256(blob).hexdigest()

entry = {
  "ts_unix": int(time.time()),
  "stamp": stamp,
  "sha256": h,
  "kappa": kappa,
  "bound_radius_est": bound_radius,
  "final_x": out["final_x"],
  "drift_D": out["drift_D"],
  "coherence_C": out["coherence_C"],
  "stability_S": out["stability_S"],
  "lambda_c": args.lambda_c,
  "alpha": args.alpha,
  "rho": args.rho,
  "Umax": args.Umax,
  "steps": args.steps,
  "gamma": args.gamma
}

with open(ledger_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry) + "\n")

print(json.dumps(entry, indent=2))
print("STATE_PATH:", state_path)
