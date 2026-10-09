#!/usr/bin/env python3
"""Build Kyous_full_YYYYMMDD.yaml with all classical rules inlined (no HTTP rule-providers)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "rules"
OUT_DIR = ROOT / "release"

CLASSICAL = [
    "SteamCN", "Steam", "Download", "Lan", "Lan_CN", "China", "Apple", "ChinaMedia",
    "Bilibili", "Firefox", "Microsoft", "OneDrive", "GPT_AI", "Google", "GoogleDrive",
    "Github", "Developer", "Telegram", "YouTube", "Netflix", "Bahamut", "GlobalMedia",
    "Twitter", "media_sites",
]

FILE_MAP = {
    "media_sites": "media_sites.yaml",
    "Lan_CN": "Lan_CN.yaml",
    "ChinaMedia": "ChinaMedia.yaml",
    "GlobalMedia": "GlobalMedia.yaml",
    "GoogleDrive": "GoogleDrive.yaml",
    "GPT_AI": "GPT_AI.yaml",
    "SteamCN": "SteamCN.yaml",
}


def load_classical(path: Path) -> list[str]:
    if not path.exists():
        return []
    out: list[str] = []
    for ln in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = ln.strip()
        if not s or s.startswith("#") or s in ("---", "...") or s.startswith("payload:"):
            continue
        if s.endswith(":") and not s[0].isupper():
            continue
        if s.startswith("- "):
            s = s[2:].strip().strip("'\"")
        if s.startswith("DOMAIN") or s.startswith("IP-") or s.startswith("GEOIP") or s.startswith("PROCESS") or s.startswith("DST-") or s.startswith("SRC-") or s.startswith("NETWORK") or s.startswith("UID"):
            out.append(s)
        elif "." in s and "," not in s and " " not in s:
            out.append(f"DOMAIN-SUFFIX,{s}")
        elif "," in s:
            out.append(s)
    return out


def load_domains(path: Path) -> list[str]:
    if not path.exists():
        return []
    out: list[str] = []
    for ln in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("- "):
            s = s[2:].strip().strip("'\"")
        if s.startswith("DOMAIN-SUFFIX,"):
            s = s.split(",", 1)[1].strip()
        elif s.startswith("DOMAIN,"):
            s = s.split(",", 1)[1].strip()
        elif "," in s:
            continue
        if "." in s:
            out.append(s)
    return out


def main() -> None:
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    version = f"Kyous-{date}"
    stats = {}
    payloads = {}
    for name in CLASSICAL:
        fn = FILE_MAP.get(name, f"{name}.yaml")
        pl = load_classical(RULES / fn)
        payloads[name] = pl
        stats[name] = len(pl)
        print(f"{name}: {len(pl)}")

    private = load_domains(RULES / "private.yaml")
    print(f"private: {len(private)}")

    head = f"""# ============================================================
# Ryukyou full config (rules embedded, no HTTP rule-providers)
# yaml_version: {version}
# rules_version: clash-rules@{date}
# generated_utc: {datetime.now(timezone.utc).isoformat()}
# notes: docs/KYOS_NOTES_{date}.md
# ============================================================
mixed-port: 7890
allow-lan: true
mode: rule
log-level: info
ipv6: false
tcp-concurrent: true
unified-delay: true
profile:
  store-selected: true
  store-fake-ip: true

tun:
  enable: true
  stack: mixed
  mtu: 9000
  dns-hijack:
    - any:53
    - tcp://any:53
    - 0.0.0.0:53
  auto-detect-interface: true
  auto-route: true
  auto-redirect: true
  strict-route: true

sniffer:
  enable: true
  override-destination: true
  parse-pure-ip: true
  force-dns-mapping: true
  sniff:
    HTTP:
      ports: [80, 8080-8880]
    TLS:
      ports: [443, 8443]
    QUIC:
      ports: [443]

dns:
  enable: true
  listen: 0.0.0.0:1053
  ipv6: false
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.0/16
  use-system-hosts: false
  prefer-h3: false
  respect-rules: true
  default-nameserver:
    - 223.5.5.5
    - 119.29.29.29
    - 8.8.8.8
  proxy-server-nameserver:
    - https://doh.pub/dns-query
    - https://dns.alidns.com/dns-query
  direct-nameserver:
    - https://doh.pub/dns-query
    - https://dns.alidns.com/dns-query
  nameserver:
    - https://1.1.1.1/dns-query
    - https://dns.google/dns-query
  fallback:
    - https://1.1.1.1/dns-query
    - https://dns.google/dns-query
    - tls://8.8.8.8:853
  nameserver-policy:
    "geosite:cn":
      - https://doh.pub/dns-query
      - https://dns.alidns.com/dns-query
    "geosite:geolocation-!cn":
      - https://1.1.1.1/dns-query
      - https://dns.google/dns-query
    "+.msftconnecttest.com": system
    "+.msftncsi.com": system
  fallback-filter:
    geoip: true
    geoip-code: CN
    ipcidr:
      - 240.0.0.0/4
  fake-ip-filter:
    - "*.lan"
    - "*.local"
    - "*.localhost"
    - "+.ts.net"
    - "time.windows.com"
    - "time.nist.gov"
    - "*.ntp.org"
    - "+.msftconnecttest.com"
    - "+.msftncsi.com"
    - "localhost.ptlogin2.qq.com"
    - "localhost.sec.qq.com"
    - "+.stun.*.*"
    - "+.stun.*.*.*"

proxy-providers:
  free-sub:
    type: http
    url: "https://gitlab.com/free9999/ipupdate/-/raw/master/backup/img/1/2/ipp/quick/1/config.yaml"
    interval: 3600
    path: ./providers/free-sub.yaml
    health-check:
      enable: true
      url: https://www.gstatic.com/generate_204
      interval: 300
    override:
      additional-prefix: "[Free] "
  daily-nodes:
    type: http
    url: "https://raw.githubusercontent.com/RyuKyou/calendar-update-system/main/output/clash_clean.yaml"
    interval: 3600
    path: ./providers/daily-nodes.yaml
    health-check:
      enable: true
      url: https://www.gstatic.com/generate_204
      interval: 300
    override:
      additional-prefix: "[Daily] "
  FQ:
    type: http
    url: "https://www.67867867.xyz/Alvin9999/PAC/refs/heads/master/backup/img/1/2/ipp/quick/1/config.yaml"
    interval: 3600
    path: ./providers/FQ.yaml
    health-check:
      enable: true
      url: https://www.gstatic.com/generate_204
      interval: 300
    override:
      additional-prefix: "[FQ] "

proxy-groups:
  - name: 🐟 漏网之鱼
    type: select
    include-all: true
    proxies: [DIRECT, 🚀 故障轉移, ♻️ 自动选择, 🚀 手动切换]
  - name: 🚀 手动切换
    type: select
    include-all: true
    proxies: [♻️ 自动选择, 🚀 故障轉移, ⚖️ 負載均衡, DIRECT]
  - name: 🤖 AI
    type: select
    include-all: true
    proxies: [♻️ 自动选择, 🚀 手动切换, 🚀 故障轉移, DIRECT, REJECT]
  - name: 🎮 Steam
    type: select
    proxies: [🚀 手动切换, ♻️ 自动选择, 🚀 故障轉移, DIRECT]
  - name: 🎮 Steam下载
    type: select
    proxies: [DIRECT, 🎮 Steam, 🚀 手动切换, ♻️ 自动选择]
  - name: 🔞 Porn
    type: select
    include-all: true
    proxies: [🔞 RFT, 🚀 手动切换, ♻️ 自动选择, 🚀 故障轉移, REJECT, DIRECT]
  - name: 🛑 广告屏蔽
    type: select
    proxies: [REJECT, 🚀 手动切换, ♻️ 自动选择, DIRECT]
  - name: Microsoft
    type: select
    proxies: [DIRECT, 🚀 手动切换, ♻️ 自动选择]
  - name: 🎯 全球直连/版权区
    type: select
    proxies: [DIRECT, 🚀 手动切换]
  - name: ♻️ 自动选择
    type: url-test
    include-all: true
    url: https://www.gstatic.com/generate_204
    interval: 300
    tolerance: 50
    lazy: true
  - name: 🔞 RFT
    type: url-test
    include-all: true
    exclude-type: "ss|ssr|shadowsocks|vmess|http|socks5|hysteria|tuic|wireguard|anytls|snell"
    filter: "(?i)US|UK|NL|DE|CA|KR|SG|JP"
    url: https://www.gstatic.com/generate_204
    interval: 300
    tolerance: 50
    lazy: true
  - name: 🚀 故障轉移
    type: fallback
    include-all: true
    url: https://www.gstatic.com/generate_204
    interval: 300
    tolerance: 50
  - name: ⚖️ 負載均衡
    type: load-balance
    strategy: consistent-hashing
    include-all: true
    url: https://www.gstatic.com/generate_204
    interval: 3600
    tolerance: 50

"""

    rp = ["# ========== embedded rule-providers (inline) ==========", "rule-providers:"]
    for name in CLASSICAL:
        rp.append(f"  {name}:")
        rp.append("    type: inline")
        rp.append("    behavior: classical")
        rp.append("    payload:")
        for item in payloads[name]:
            if ":" in item or item.startswith("*"):
                rp.append(f'      - "{item}"')
            else:
                rp.append(f"      - {item}")
    rp.append("  private:")
    rp.append("    type: inline")
    rp.append("    behavior: domain")
    rp.append("    payload:")
    for d in private:
        rp.append(f"      - {d}")
    rp.append(f"# stats: {stats}")
    rp.append("# skipped binary: adblock.mrs category-ai.mrs")

    rules = """
rules:
  - IP-CIDR,192.168.0.0/16,DIRECT,no-resolve
  - IP-CIDR,10.0.0.0/8,DIRECT,no-resolve
  - IP-CIDR,172.16.0.0/12,DIRECT,no-resolve
  - IP-CIDR,127.0.0.0/8,DIRECT,no-resolve
  - IP-CIDR,100.64.0.0/10,DIRECT,no-resolve
  - IP-CIDR,224.0.0.0/4,DIRECT,no-resolve
  - IP-CIDR6,fe80::/10,DIRECT,no-resolve
  - DOMAIN-SUFFIX,local,DIRECT
  - DOMAIN-SUFFIX,localhost,DIRECT
  - DOMAIN-SUFFIX,lan,DIRECT
  - DOMAIN-SUFFIX,ts.net,DIRECT
  - DOMAIN-SUFFIX,tailscale.com,DIRECT
  - IP-CIDR,3.36.170.245/32,🤖 AI,no-resolve
  - DST-PORT,20000,🤖 AI
  - DOMAIN-SUFFIX,windowsupdate.com,Microsoft
  - DOMAIN-SUFFIX,update.microsoft.com,Microsoft
  - DOMAIN-SUFFIX,download.microsoft.com,Microsoft
  - DOMAIN-SUFFIX,microsoft.com,Microsoft
  - DOMAIN-SUFFIX,office.com,Microsoft
  - DOMAIN-SUFFIX,live.com,Microsoft
  - DOMAIN-SUFFIX,msftncsi.com,Microsoft
  - DOMAIN-SUFFIX,msftconnecttest.com,Microsoft
  - RULE-SET,SteamCN,DIRECT
  - RULE-SET,Steam,🎮 Steam
  - DOMAIN-SUFFIX,steamcontent.com,🎮 Steam下载
  - DOMAIN-SUFFIX,steamserver.net,🎮 Steam下载
  - DOMAIN-SUFFIX,steampowered.com,🎮 Steam
  - DOMAIN-SUFFIX,steamcommunity.com,🎮 Steam
  - DOMAIN-SUFFIX,steamstatic.com,🎮 Steam
  - RULE-SET,media_sites,🔞 Porn
  - DOMAIN-SUFFIX,xhamster.com,🔞 Porn
  - DOMAIN-SUFFIX,xhcdn.com,🔞 Porn
  - DOMAIN-SUFFIX,t66y.com,🔞 Porn
  - DOMAIN-SUFFIX,hitomi.la,🔞 Porn
  - DOMAIN-SUFFIX,anime1.me,🚀 手动切换
  - DOMAIN-SUFFIX,anime1.pw,🚀 手动切换
  - RULE-SET,Download,DIRECT
  - RULE-SET,Lan,DIRECT
  - RULE-SET,Lan_CN,DIRECT
  - RULE-SET,private,DIRECT
  - RULE-SET,China,DIRECT
  - RULE-SET,Apple,DIRECT
  - RULE-SET,ChinaMedia,DIRECT
  - RULE-SET,Bilibili,🎯 全球直连/版权区
  - RULE-SET,Firefox,DIRECT
  - RULE-SET,Microsoft,Microsoft
  - RULE-SET,OneDrive,🚀 手动切换
  - RULE-SET,GPT_AI,🤖 AI
  - DOMAIN-SUFFIX,x.ai,🤖 AI
  - DOMAIN-SUFFIX,grok.com,🤖 AI
  - DOMAIN-SUFFIX,grok.x.ai,🤖 AI
  - DOMAIN-KEYWORD,xai,🤖 AI
  - RULE-SET,Google,🚀 手动切换
  - RULE-SET,GoogleDrive,🚀 手动切换
  - RULE-SET,Github,🚀 手动切换
  - RULE-SET,Developer,🚀 手动切换
  - RULE-SET,Telegram,🚀 手动切换
  - RULE-SET,YouTube,🚀 手动切换
  - RULE-SET,Netflix,🚀 手动切换
  - RULE-SET,Bahamut,🚀 手动切换
  - RULE-SET,GlobalMedia,🚀 手动切换
  - RULE-SET,Twitter,🚀 手动切换
  - GEOIP,CN,DIRECT,no-resolve
  - MATCH,🐟 漏网之鱼
"""

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"Kyous_full_{date}.yaml"
    text = head + "\n".join(rp) + "\n" + rules
    out.write_text(text, encoding="utf-8")
    # stable name for clients
    (OUT_DIR / "Kyous_full_latest.yaml").write_text(text, encoding="utf-8")
    print(f"Wrote {out} ({len(text)} bytes)")


if __name__ == "__main__":
    main()
