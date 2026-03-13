<p align="center">
  <img src="./assets/profile-header.svg" width="100%" alt="byteD-x 主页头图" />
</p>

<p align="center">
  <a href="mailto:2041487752dxj@gmail.com">
    <img src="https://img.shields.io/badge/邮箱-2041487752dxj%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="邮箱" />
  </a>
  <a href="https://github.com/byteD-x">
    <img src="https://img.shields.io/badge/GitHub-@byteD--x-18181B?style=flat-square&logo=github&logoColor=white" alt="GitHub" />
  </a>
  <a href="https://my-resume-gray-five.vercel.app/">
    <img src="https://img.shields.io/badge/作品集-在线访问-2563EB?style=flat-square&logo=vercel&logoColor=white" alt="作品集" />
  </a>
  <img src="https://img.shields.io/badge/微信-w2041487752-07C160?style=flat-square&logo=wechat&logoColor=white" alt="微信" />
  <img src="https://img.shields.io/badge/状态-可交流合作-18181B?style=flat-square" alt="状态" />
</p>

```text
你好，我是 byteD-x。

AI 应用工程师，专注 RAG、Agent、多模态 AI 与生产级系统落地。
我更关心真实业务场景里的稳定性、成本、可观测性和可验证结果。
```

## 我在做什么

我专注把 LLM 能力接到真实业务里，做的是能上线、能观测、能回归、能解释的 AI 系统。

| 方向 | 我实际在做什么 |
| --- | --- |
| 检索与编排 | 混合检索、引用链路、LangGraph 工作流、可恢复执行 |
| 多模态接入 | 文本 / 语音 / RTC 接入、业务工具调用、Auth Bridge、人工接管 |
| 性能与成本 | 提速、缓存治理、Token 成本压缩、评测回归、稳定性基线 |

## 我做的系统长什么样

```mermaid
flowchart LR
    U["用户 / 渠道"] --> I["接入层<br/>文本 | 语音 | RTC"]
    I --> O["编排层<br/>LangGraph / Workflow"]
    O --> R["检索层<br/>混合检索 / 重排 / 引用溯源"]
    O --> T["工具层<br/>鉴权桥接 / 业务 API"]
    O --> H["人工协同<br/>中断 / 恢复 / 转人工"]
    R --> A["回答 / 执行动作"]
    T --> A
    H --> A
    A --> F["反馈 / 评测 / 回归"]
    F --> O
```

## 技术栈

**核心栈**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![AsyncIO](https://img.shields.io/badge/AsyncIO-18181B?style=flat-square&logoColor=white)
![Java 21](https://img.shields.io/badge/Java%2021-007396?style=flat-square&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring%20Boot%203.x-6DB33F?style=flat-square&logo=spring-boot&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-18181B?style=flat-square&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-EA5A25?style=flat-square&logo=qdrant&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)

**交付栈**

![Next.js](https://img.shields.io/badge/Next.js-18181B?style=flat-square&logo=next.js&logoColor=white)
![Vue 3](https://img.shields.io/badge/Vue%203-4FC08D?style=flat-square&logo=vue.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white)
![ClickHouse](https://img.shields.io/badge/ClickHouse-FFCC01?style=flat-square&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white)

**也做过这些**

![Go](https://img.shields.io/badge/Go-00ADD8?style=flat-square&logo=go&logoColor=white)
![Elasticsearch](https://img.shields.io/badge/Elasticsearch-005571?style=flat-square&logo=elasticsearch&logoColor=white)
![Kafka](https://img.shields.io/badge/Kafka-231F20?style=flat-square&logo=apache-kafka&logoColor=white)
![Electron](https://img.shields.io/badge/Electron-47848F?style=flat-square&logo=electron&logoColor=white)

## 代表项目

<table>
  <tr>
    <td width="50%" valign="top">
      <strong><a href="https://github.com/byteD-x/customer-ai-runtime">customer-ai-runtime</a></strong><br />
      企业级智能客服运行时，支持文本 / 语音 / RTC，多渠道接入与人工协同接管。<br /><br />
      <code>Python</code> <code>FastAPI</code> <code>AsyncIO</code> <code>LangGraph</code> <code>Qdrant</code><br /><br />
      <img src="https://img.shields.io/github/stars/byteD-x/customer-ai-runtime?style=flat-square&label=Star&color=18181B" alt="customer-ai-runtime stars" />
      <img src="https://img.shields.io/github/last-commit/byteD-x/customer-ai-runtime?style=flat-square&label=最近更新&color=2563EB" alt="customer-ai-runtime updated" />
    </td>
    <td width="50%" valign="top">
      <strong><a href="https://github.com/byteD-x/rag-qa-system">rag-qa-system</a></strong><br />
      企业知识问答平台，多源文档接入、混合检索、答案引用溯源与评测回归。<br /><br />
      <code>Python</code> <code>FastAPI</code> <code>LangGraph</code> <code>PostgreSQL</code> <code>Vue 3</code><br /><br />
      <img src="https://img.shields.io/github/stars/byteD-x/rag-qa-system?style=flat-square&label=Star&color=18181B" alt="rag-qa-system stars" />
      <img src="https://img.shields.io/github/last-commit/byteD-x/rag-qa-system?style=flat-square&label=最近更新&color=2563EB" alt="rag-qa-system updated" />
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <strong><a href="https://github.com/byteD-x/wechat-bot">wechat-bot</a></strong><br />
      微信 PC 端 AI 助手，包含长期记忆、多模型支持、情感识别与 Electron 管理端。<br /><br />
      <code>Python</code> <code>Quart</code> <code>AsyncIO</code> <code>Electron</code> <code>wxauto</code><br /><br />
      <img src="https://img.shields.io/github/stars/byteD-x/wechat-bot?style=flat-square&label=Star&color=18181B" alt="wechat-bot stars" />
      <img src="https://img.shields.io/github/last-commit/byteD-x/wechat-bot?style=flat-square&label=最近更新&color=2563EB" alt="wechat-bot updated" />
    </td>
    <td width="50%" valign="top">
      <strong><a href="https://github.com/byteD-x/easyCloudPan">easyCloudPan</a></strong><br />
      企业级网盘系统，前后端分离、多租户隔离、完整权限体系与高性能上传。<br /><br />
      <code>Java 21</code> <code>Spring Boot 3.x</code> <code>Vue 3</code> <code>React 19</code><br /><br />
      <img src="https://img.shields.io/github/stars/byteD-x/easyCloudPan?style=flat-square&label=Star&color=18181B" alt="easyCloudPan stars" />
      <img src="https://img.shields.io/github/last-commit/byteD-x/easyCloudPan?style=flat-square&label=最近更新&color=2563EB" alt="easyCloudPan updated" />
    </td>
  </tr>
</table>

## 做出过的结果

这些不是“会一点”的技能标签，而是做过并留下结果的工程信号。

| 事项 | 结果 |
| --- | --- |
| 报表性能优化 | `20s+ -> 4s`，约 `5x` 提速 |
| AI 成本优化 | Token 成本下降 `40%` |
| 数据迁移 | `300+` 表、`3e8+` 记录无损迁移 |
| 交付方式 | 从需求澄清到上线闭环，强调回归与可验证性 |

## 职业经历

| 时间 | 角色 | 事项 |
| --- | --- | --- |
| `2026.02 - 至今` | 独立开发者 | 持续开发智能客服运行时、RAG-QA 系统、微信 AI 助手等开源项目 |
| `2025.11 - 2025.12` | 外包技术顾问 @ 南方科技大学 | 智能流程自动化原型，从需求澄清到闭环交付 |
| `2025.04 - 2025.09` | 后端 / 全栈工程师 @ 中软国际 | 企业知识问答系统研发，负责 RAG 设计、LangGraph 运行时、评测回归 |
| `2024.08 - 2024.10` | 后端开发实习生 @ 国家骨科临床研究中心 | 论文检索小程序后端，AI 搜索与订阅推送 |
| `2024.05 - 2024.08` | 后端开发实习生 @ 中国联通陕西省分公司 | 运营平台建设，性能优化与大规模数据迁移 |
| `2024.04 - 2026.02` | 全栈开发 @ 开源项目 | EasyCloudPan 网盘系统开发与维护 |

## GitHub 活跃轨迹

### 🐍 提交贡献蛇形动画

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/byteD-x/byteD-x/blob/output/github-contribution-grid-snake-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/byteD-x/byteD-x/blob/output/github-contribution-grid-snake.svg" />
    <img alt="GitHub contribution snake" src="https://github.com/byteD-x/byteD-x/blob/output/github-contribution-grid-snake.svg" width="100%" />
  </picture>
</p>

### 📊 活动统计

<p align="center">
  <a href="https://github.com/ashutosh00710/github-readme-activity-graph">
    <img alt="Activity Graph" src="https://github-readme-activity-graph.vercel.app/graph?username=byteD-x&theme=github-dark&hide_border=true&area=true&point=00ff00&line=00ff00&radius=16" width="100%" />
  </a>
</p>

### 🔥 贡献热度

<p align="center">
  <a href="https://git.io/streak-stats">
    <img alt="GitHub Streak Stats" src="https://github-readme-streak-stats.herokuapp.com/?user=byteD-x&theme=github-dark&hide_border=true&date_format=M%20j%5B%2C%20Y%5D" />
  </a>
</p>

<details>
  <summary><strong>联系方式</strong></summary>
  <br />

  - 邮件：`2041487752dxj@gmail.com`
  - 微信：`w2041487752`
  - GitHub：[`@byteD-x`](https://github.com/byteD-x)
  - 作品集：[`my-resume-gray-five.vercel.app`](https://my-resume-gray-five.vercel.app/)
  - 合作方向：`RAG / Agent`、`LLM 生产化`、`性能优化`、`技术咨询`
</details>

---

<p align="center">
  <code>最后更新：2026-03-13</code>
</p>
