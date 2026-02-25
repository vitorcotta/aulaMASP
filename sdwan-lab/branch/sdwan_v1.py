import subprocess
import time
from pathlib import Path

LOG_FILE = Path("/logs/sdwan_branch.log")

HUB_OVER_GRE1 = "192.168.10.2"
HUB_OVER_GRE2 = "192.168.20.2"
APP_NET = "10.20.0.0/24"

PING_COUNT = 3
INTERVAL_SEC = 3


def ping_rtt(target: str) -> float:
  try:
    out = subprocess.check_output(
      ["ping", "-c", str(PING_COUNT), "-n", "-q", target],
      stderr=subprocess.DEVNULL,
      text=True,
      timeout=5,
    )
  except Exception:
    return float("inf")

  for line in out.splitlines():
    if "rtt min/avg/max" in line or "round-trip min/avg/max" in line:
      stats = line.split("=")[1].strip().split()[0]
      _, avg, _, _ = stats.split("/")
      return float(avg)
  return float("inf")


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
  log("SDWAN_V1 start (flapping expected)")

  while True:
    rtt1 = ping_rtt(HUB_OVER_GRE1)
    rtt2 = ping_rtt(HUB_OVER_GRE2)
    log(f"RTT gre1={rtt1:.2f}ms gre2={rtt2:.2f}ms")

    # Algoritmo simples: escolhe sempre o menor RTT → sujeito a flapping
    if rtt1 <= rtt2:
      desired = "gre1"
      via = HUB_OVER_GRE1
    else:
      desired = "gre2"
      via = HUB_OVER_GRE2

    if desired != active:
      active = desired
      set_route(via, active)
      log(f"ACTIVE_PATH {active} via {via}")

    time.sleep(INTERVAL_SEC)


if __name__ == "__main__":
  main()

