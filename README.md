<h1 align="center">byteD-x</h1>

<p align="center">
  <strong>AI Systems / RAG / Agent Engineering / Backend & Full Stack</strong>
</p>

<p align="center">
  构建可恢复、可追踪、可评测的 AI 应用与工程基础设施。
</p>

<p align="center">
  <a href="mailto:2041487752dxj@gmail.com">
    <img src="https://img.shields.io/badge/Email-2041487752dxj%40gmail.com-18181B?style=for-the-badge&logo=minutemailer&logoColor=60A5FA" alt="邮箱" />
  </a>
  <a href="https://github.com/byteD-x">
    <img src="https://img.shields.io/badge/GitHub-@byteD--x-18181B?style=for-the-badge&logo=github&logoColor=60A5FA" alt="GitHub" />
  </a>
  <a href="https://my-resume-gray-five.vercel.app/">
    <img src="https://img.shields.io/badge/Portfolio-Online-18181B?style=for-the-badge&logo=vercel&logoColor=60A5FA" alt="作品集" />
  </a>
  <img src="https://img.shields.io/badge/WeChat-w2041487752-18181B?style=for-the-badge&logo=wechat&logoColor=60A5FA" alt="微信" />
  <img src="https://img.shields.io/badge/Status-Available-18181B?style=for-the-badge&logo=statuspage&logoColor=34D399" alt="状态" />
</p>

<br>

### 核心聚焦

<table>
  <tr>
    <td width="33%" valign="top">
      <h4>检索与编排</h4>
      <p style="font-size: 14px; color: #52525B;">混合检索、引用链路溯源、LangGraph 工作流、可恢复执行的 Agent 架构。</p>
    </td>
    <td width="33%" valign="top">
      <h4>多模态与协同</h4>
      <p style="font-size: 14px; color: #52525B;">文本 / 语音 / RTC 全渠道接入、业务工具调用、Auth Bridge 与人工接管机制。</p>
    </td>
    <td width="33%" valign="top">
      <h4>性能与治理</h4>
      <p style="font-size: 14px; color: #52525B;">系统提速、缓存治理、Token 成本压缩 40%+、评测回归体系与稳定性基线建设。</p>
    </td>
  </tr>
</table>

### 架构视图

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#F8FAFC', 'primaryTextColor': '#09090B', 'primaryBorderColor': '#94A3B8', 'lineColor': '#64748B', 'secondaryColor': '#F1F5F9', 'tertiaryColor': '#E2E8F0', 'fontFamily': 'Space Mono, Consolas, monospace'}}}%%
flowchart LR
    U(["用户请求"]) --> I["接入网关"]
    I --> O["编排引擎"]
    O --> R["混合检索"]
    O --> T["业务工具"]
    O --> H["人工协同"]
    R --> A["生成闭环"]
    T --> A
    H --> A
    A --> F["评测反馈"]
    F -.-> O
    
    style U fill:#18181B,stroke:#3F3F46,stroke-width:2px,color:#FAFAFA
    style I fill:#EFF6FF,stroke:#BFDBFE,stroke-width:2px,color:#1E3A8A
    style O fill:#EEF2FF,stroke:#C7D2FE,stroke-width:2px,color:#312E81
    style R fill:#F0FDF4,stroke:#BBF7D0,stroke-width:2px,color:#14532D
    style T fill:#FEF2F2,stroke:#FECACA,stroke-width:2px,color:#7F1D1D
    style H fill:#F8FAFC,stroke:#E2E8F0,stroke-width:2px,color:#0F172A
    style A fill:#18181B,stroke:#3F3F46,stroke-width:2px,color:#FAFAFA
    style F fill:#FAFAFA,stroke:#E4E4E7,stroke-width:2px,stroke-dasharray: 5 5,color:#3F3F46
```

### 技术栈

<p>
  <b>核心架构：</b><br>
  <img src="https://img.shields.io/badge/Python-18181B?style=flat-square&logo=python&logoColor=60A5FA" />
  <img src="https://img.shields.io/badge/FastAPI-18181B?style=flat-square&logo=fastapi&logoColor=059669" />
  <img src="https://img.shields.io/badge/LangGraph-18181B?style=flat-square&logo=langchain&logoColor=FAFAFA" />
  <img src="https://img.shields.io/badge/Java_21-18181B?style=flat-square&logo=openjdk&logoColor=EA580C" />
  <img src="https://img.shields.io/badge/Spring_Boot-18181B?style=flat-square&logo=spring-boot&logoColor=6DB33F" />
  <img src="https://img.shields.io/badge/Qdrant-18181B?style=flat-square&logo=qdrant&logoColor=EA5A25" />
  <img src="https://img.shields.io/badge/PostgreSQL-18181B?style=flat-square&logo=postgresql&logoColor=60A5FA" />
</p>
<p>
  <b>交付基建：</b><br>
  <img src="https://img.shields.io/badge/TypeScript-18181B?style=flat-square&logo=typescript&logoColor=3178C6" />
  <img src="https://img.shields.io/badge/Next.js-18181B?style=flat-square&logo=next.js&logoColor=FAFAFA" />
  <img src="https://img.shields.io/badge/Vue_3-18181B?style=flat-square&logo=vue.js&logoColor=4FC08D" />
  <img src="https://img.shields.io/badge/Redis-18181B?style=flat-square&logo=redis&logoColor=DC382D" />
  <img src="https://img.shields.io/badge/Docker-18181B?style=flat-square&logo=docker&logoColor=2496ED" />
  <img src="https://img.shields.io/badge/Kubernetes-18181B?style=flat-square&logo=kubernetes&logoColor=326CE5" />
</p>

### 代表项目

<p style="font-size: 13px; color: #52525B;">
  以下内容由 GitHub 实时仓库数据自动生成，当前按星标、分叉和最近活跃度综合排序；描述信息每 15 分钟刷新一次，星标、分叉和最近提交通过动态徽章实时同步。
</p>

<!-- representative-projects:start -->
<table width="100%" style="border-collapse: collapse; border: none;">
  <tr>
    <td width="50%" valign="top" style="border: 1px solid #E4E4E7; padding: 16px;">
      <h4><a href="https://github.com/byteD-x/wechat-bot" style="color: #2563EB; text-decoration: none;">wechat-bot</a></h4>
      <p style="font-size: 13px; color: #52525B;">基于 wxauto 的微信 PC 端 AI 自动回复机器人，支持多模型 API 与各种oauth（OpenAI/DeepSeek/豆包等），支持各种coding plan (Kimi，GLM，codex team等)，内置记忆、情感识别与 Electron 可视化界面。</p>
      <code>Python</code>
      <br><br>
      <img src="https://img.shields.io/github/stars/byteD-x/wechat-bot?style=flat-square&color=2563EB&labelColor=18181B" alt="wechat-bot stars" />
      <img src="https://img.shields.io/github/forks/byteD-x/wechat-bot?style=flat-square&color=60A5FA&labelColor=18181B" alt="wechat-bot forks" />
      <img src="https://img.shields.io/github/last-commit/byteD-x/wechat-bot?style=flat-square&color=34D399&labelColor=18181B" alt="wechat-bot last commit" />
    </td>
    <td width="50%" valign="top" style="border: 1px solid #E4E4E7; padding: 16px;">
      <h4><a href="https://github.com/byteD-x/easyCloudPan" style="color: #2563EB; text-decoration: none;">easyCloudPan</a></h4>
      <p style="font-size: 13px; color: #52525B;">高性能前后端分离网盘系统，支持 Vue 3 和 React 19 双前端，基于 Java 21 虚拟线程和 Spring Boot 3.x 构建。</p>
      <code>Java</code>
      <br><br>
      <img src="https://img.shields.io/github/stars/byteD-x/easyCloudPan?style=flat-square&color=2563EB&labelColor=18181B" alt="easyCloudPan stars" />
      <img src="https://img.shields.io/github/forks/byteD-x/easyCloudPan?style=flat-square&color=60A5FA&labelColor=18181B" alt="easyCloudPan forks" />
      <img src="https://img.shields.io/github/last-commit/byteD-x/easyCloudPan?style=flat-square&color=34D399&labelColor=18181B" alt="easyCloudPan last commit" />
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top" style="border: 1px solid #E4E4E7; padding: 16px;">
      <h4><a href="https://github.com/byteD-x/rag-qa-system" style="color: #2563EB; text-decoration: none;">rag-qa-system</a></h4>
      <p style="font-size: 13px; color: #52525B;">企业级 RAG 问答系统 | 多源知识连接器 | 分片审查 | 检索调试 | 平台治理能力</p>
      <code>Python</code>
      <br><br>
      <img src="https://img.shields.io/github/stars/byteD-x/rag-qa-system?style=flat-square&color=2563EB&labelColor=18181B" alt="rag-qa-system stars" />
      <img src="https://img.shields.io/github/forks/byteD-x/rag-qa-system?style=flat-square&color=60A5FA&labelColor=18181B" alt="rag-qa-system forks" />
      <img src="https://img.shields.io/github/last-commit/byteD-x/rag-qa-system?style=flat-square&color=34D399&labelColor=18181B" alt="rag-qa-system last commit" />
    </td>
    <td width="50%" valign="top" style="border: 1px solid #E4E4E7; padding: 16px;">
      <h4><a href="https://github.com/byteD-x/customer-ai-runtime" style="color: #2563EB; text-decoration: none;">customer-ai-runtime</a></h4>
      <p style="font-size: 13px; color: #52525B;">企业级智能客服引擎，支持 RAG 知识增强、AI/人工协同、模块化接入。提供文本/语音/RTC 多渠道客服能力，可作为 FastAPI 子应用无缝集成到现有业务系统。</p>
      <code>Python</code>
      <br><br>
      <img src="https://img.shields.io/github/stars/byteD-x/customer-ai-runtime?style=flat-square&color=2563EB&labelColor=18181B" alt="customer-ai-runtime stars" />
      <img src="https://img.shields.io/github/forks/byteD-x/customer-ai-runtime?style=flat-square&color=60A5FA&labelColor=18181B" alt="customer-ai-runtime forks" />
      <img src="https://img.shields.io/github/last-commit/byteD-x/customer-ai-runtime?style=flat-square&color=34D399&labelColor=18181B" alt="customer-ai-runtime last commit" />
    </td>
  </tr>
</table>
<!-- representative-projects:end -->

### 履历与产出

<table width="100%">
  <tr>
    <th width="25%" align="left">时间线</th>
    <th width="30%" align="left">角色与组织</th>
    <th width="45%" align="left">核心产出</th>
  </tr>
  <tr>
    <td><code>2025.11 - 2025.12</code></td>
    <td>外包技术顾问<br><em>@南方科技大学</em></td>
    <td><span style="color: #3F3F46; font-size: 13px;">智能流程自动化原型开发，完成从需求澄清到架构设计的闭环交付。</span></td>
  </tr>
  <tr>
    <td><code>2025.04 - 2025.09</code></td>
    <td>后端 / 全栈工程师<br><em>@中软国际</em></td>
    <td><span style="color: #3F3F46; font-size: 13px;">企业知识问答系统研发。设计 RAG 架构与 LangGraph 运行时，Token 成本优化 <b>40%</b>。</span></td>
  </tr>
  <tr>
    <td><code>2024.08 - 2024.10</code></td>
    <td>后端实习生<br><em>@国家骨科临床研究中心</em></td>
    <td><span style="color: #3F3F46; font-size: 13px;">论文检索系统构建。实现高可用 AI 搜索与定向订阅推送闭环。</span></td>
  </tr>
  <tr>
    <td><code>2024.05 - 2024.08</code></td>
    <td>后端实习生<br><em>@中国联通陕西分公司</em></td>
    <td><span style="color: #3F3F46; font-size: 13px;">大规模数据迁移（300+表，3亿级记录）。报表查询性能优化 <b>5x</b>（20s -> 4s）。</span></td>
  </tr>
</table>

### 活动指标

<div align="center">

<img src="https://github-profile-summary-cards.vercel.app/api/cards/stats?username=byteD-x&theme=github" width="49%" />
<img src="https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=byteD-x&theme=github" width="49%" />

<br>

</div>

<br>

### Pixel Arcade // Contribution Grid

<p align="center">
  <img src="assets/github-contribution-grid-snake-arcade.svg" alt="byteD-x pixel arcade contribution snake preview" />
</p>

<br>

<p align="center">
  <code style="color: #A1A1AA;">systemctl status byteD-x --no-pager</code>
</p>
