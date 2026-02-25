import math
import subprocess
import time
from pathlib import Path

LOG_FILE = Path("/logs/sdwan_branch.log")

HUB_OVER_GRE1 = "192.168.10.2"
HUB_OVER_GRE2 = "192.168.20.2"
APP_NET = "10.20.0.0/24"

PING_COUNT = 3
INTERVAL_SEC = 3

# Parâmetros de histerese / hold-down
BETTER_THRESHOLD = 0.10  # 10% melhor
REQUIRED_CONSECUTIVE = 3
HOLD_DOWN_SEC = 20


def ping_stats(target: str) -> tuple[float, float]:
  """
  Retorna (avg_rtt_ms, jitter_ms simples).
  """
  try:
    out = subprocess.check_output(
      ["ping", "-c", str(PING_COUNT), "-n", "-q", target],
      stderr=subprocess.DEVNULL,
      text=True,
      timeout=5,
    )
  except Exception:
    return float("inf"), float("inf")

  avg = float("inf")
  min_r = max_r = None
  for line in out.splitlines():
    if "rtt min/avg/max" in line or "round-trip min/avg/max" in line:
      stats = line.split("=")[1].strip().split()[0]
      min_s, avg_s, max_s, _ = stats.split("/")
      min_r = float(min_s)
      avg = float(avg_s)
      max_r = float(max_s)
      break
  if min_r is None or max_r is None:
    return float("inf"), float("inf")
  jitter = (max_r - min_r) / 2.0
  return avg, jitter


def link_score(avg_ms: float, jitter_ms: float) -> float:
  # Score composto simples: menor é melhor
  return avg_ms + 0.5 * jitter_ms


def set_route(via: str, dev: str):
  subprocess.run(
    ["ip", "route", "replace", APP_NET, "via", via, "dev", dev],
    check=False,
  )


def log(line: str):
  ts = time.strftime("%Y-%m-%d %H:%M:%S")
  LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
  with LOG_FILE.open("a", encoding="utf-8") as f:
    f.write(f"{ts} {line}\n")


def main():
  active = "gre1"
  last_switch_ts = 0.0
  candidate = None
  candidate_count = 0

  log("SDWAN_V2 start (histerese + hold-down)")

  while True:
    avg1, jit1 = ping_stats(HUB_OVER_GRE1)
    avg2, jit2 = ping_stats(HUB_OVER_GRE2)
    score1 = link_score(avg1, jit1)
    score2 = link_score(avg2, jit2)

    log(
      f"STATS gre1 avg={avg1:.2f}ms jitter={jit1:.2f}ms score={score1:.2f} "
      f"gre2 avg={avg2:.2f}ms jitter={jit2:.2f}ms score={score2:.2f}"
    )

    now = time.time()
    if now - last_switch_ts < HOLD_DOWN_SEC:
      # Em período de hold-down, não troca
      time.sleep(INTERVAL_SEC)
      continue

    # Determina melhor link pelo score
    if score1 <= score2:
      best = "gre1"
      best_score = score1
      other_score = score2
      via = HUB_OVER_GRE1
    else:
      best = "gre2"
      best_score = score2
      other_score = score1
      via = HUB_OVER_GRE2

    if best == active:
      # Já estamos no melhor, zera candidato
      candidate = None
      candidate_count = 0
    else:
      # Verifica se é suficientemente melhor (X%)
      if other_score == float("inf") or best_score == float("inf"):
        improvement = 0.0
      else:
        improvement = (other_score - best_score) / other_score

      if improvement >= BETTER_THRESHOLD:
        if candidate == best:
          candidate_count += 1
        else:
          candidate = best
          candidate_count = 1

        log(
          f"CANDIDATE {best} improvement={improvement:.2%} "
          f"count={candidate_count}/{REQUIRED_CONSECUTIVE}"
        )

        if candidate_count >= REQUIRED_CONSECUTIVE:
          # Troca efetiva
          active = best
          set_route(via, active)
          last_switch_ts = now
          log(f"ACTIVE_PATH {active} via {via} (V2 switch)")
          candidate = None
          candidate_count = 0
      else:
        # Melhorou, mas não o suficiente
        candidate = None
        candidate_count = 0

    time.sleep(INTERVAL_SEC)


if __name__ == "__main__":
  main()

