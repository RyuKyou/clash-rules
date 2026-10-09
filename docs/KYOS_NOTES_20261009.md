# Kyous 配置归档说明（2026-10-09）

## 版本

| 项 | 值 |
|----|-----|
| yaml_version | Kyous-20261009 |
| rules_version | clash-rules@20261009 |
| 文件 | `release/Kyous_full_20261009.yaml` |
| 体积约 | ~220KB |

## 下载

- https://raw.githubusercontent.com/RyuKyou/clash-rules/main/release/Kyous_full_20261009.yaml
- 网页目录：https://github.com/RyuKyou/clash-rules/tree/main/release

## 本轮结论（对话整理）

### 1. 规则集更新失败（EOF / CONNECTION_CLOSED）

- **现象**：Nikki 更新规则时 `Get ... EOF`；浏览器访问 `cdn.jsdelivr.net` 出现 `ERR_CONNECTION_CLOSED`。
- **原因**：不是单纯 DNS 配错，而是 **GitHub raw / jsDelivr 在部分网络下被干扰或重置**；含大量敏感域名的规则文件更易中招。
- **其它规则能更新、仅个别失败**：符合「内容/路径 + CDN 链路」问题。

### 2. 是否必须开全局魔法？

- **不必**为更新规则长期开全局。
- 给单条 `rule-providers` 加 `proxy:` 只方便已能翻墙的路由，其它设备仍可能直连失败。
- **治本**：规则 **inline 内嵌 / 打进主配置**，避免运行时二次 HTTP 拉规则。

### 3. 架构选择

| 方案 | 结论 |
|------|------|
| jsDelivr / GitHub raw 当规则源 | 不可靠，不作唯一依赖 |
| 每条 rule-provider 加 proxy | 仅治路由器 |
| **规则 inline / 打进主 YAML** | **采用** |
| 节点仍用 proxy-providers | 保留 free-sub / daily-nodes / FQ |

### 4. 本文件配置要点

- **前半**：端口、TUN、DNS、订阅、策略组（常改）。
- **后半**：`rule-providers`（全部 `type: inline`）+ `rules`（最后，少改）。
- **media_sites**：约 1333 条，走 `🔞 Porn`。
- **未内嵌**：`adblock.mrs`、`category-ai.mrs`（二进制）；AI 已有 GPT_AI + x.ai/grok 手工规则。

### 5. 节点侧（calendar-update-system）

- 上限 512；优先美/加/挪/新；协议 anytls → hy2 → vless → trojan；ss/vmess/ssr 最后。
- 剔除港澳；仅 TCP 可达。
- 订阅：https://raw.githubusercontent.com/RyuKyou/calendar-update-system/main/output/clash_clean.yaml

### 6. 使用方式

1. 下载 YAML，导入 Nikki / Mihomo。
2. 更新三个节点订阅。
3. **无需**再更新 HTTP 规则集。

### 7. 说明

- 个人设备分流与订阅聚合；Git 仅托管静态配置。

归档日期：2026-10-09
