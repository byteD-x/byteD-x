<p align="center">
  <img src="./assets/profile-header.svg" width="100%" alt="byteD-x 主页头图" />
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

<div align="center">
  <img src="./assets/profile-typing.svg" alt="byteD-x 简介横幅" style="max-width: 100%; height: auto;" />
</div>

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

<table width="100%" style="border-collapse: collapse; border: none;">
  <tr>
    <td width="50%" valign="top" style="border: 1px solid #E4E4E7; padding: 16px;">
      <h4><a href="https://github.com/byteD-x/customer-ai-runtime" style="color: #2563EB; text-decoration: none;">customer-ai-runtime</a></h4>
      <p style="font-size: 13px; color: #52525B;">企业级智能客服运行时。支持文本、语音、RTC 多渠道接入与人工协同接管。</p>
      <code>Python</code> <code>LangGraph</code> <code>Qdrant</code>
      <br><br>
      <img src="https://img.shields.io/github/stars/byteD-x/customer-ai-runtime?style=flat-square&color=2563EB&labelColor=18181B" />
    </td>
    <td width="50%" valign="top" style="border: 1px solid #E4E4E7; padding: 16px;">
      <h4><a href="https://github.com/byteD-x/rag-qa-system" style="color: #2563EB; text-decoration: none;">rag-qa-system</a></h4>
      <p style="font-size: 13px; color: #52525B;">企业知识问答平台。多源文档接入、混合检索、答案引用溯源与评测回归。</p>
      <code>FastAPI</code> <code>PostgreSQL</code> <code>Vue 3</code>
      <br><br>
      <img src="https://img.shields.io/github/stars/byteD-x/rag-qa-system?style=flat-square&color=2563EB&labelColor=18181B" />
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top" style="border: 1px solid #E4E4E7; padding: 16px;">
      <h4><a href="https://github.com/byteD-x/wechat-bot" style="color: #2563EB; text-decoration: none;">wechat-bot</a></h4>
      <p style="font-size: 13px; color: #52525B;">微信 PC 端 AI 助手。包含长期记忆、多模型路由、情感识别与管理后台。</p>
      <code>AsyncIO</code> <code>Electron</code> <code>wxauto</code>
      <br><br>
      <img src="https://img.shields.io/github/stars/byteD-x/wechat-bot?style=flat-square&color=2563EB&labelColor=18181B" />
    </td>
    <td width="50%" valign="top" style="border: 1px solid #E4E4E7; padding: 16px;">
      <h4><a href="https://github.com/byteD-x/easyCloudPan" style="color: #2563EB; text-decoration: none;">easyCloudPan</a></h4>
      <p style="font-size: 13px; color: #52525B;">企业级网盘系统。多租户隔离、完整权限体系与高性能分片上传。</p>
      <code>Spring Boot</code> <code>React 19</code>
      <br><br>
      <img src="https://img.shields.io/github/stars/byteD-x/easyCloudPan?style=flat-square&color=2563EB&labelColor=18181B" />
    </td>
  </tr>
</table>

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

<img src="https://github-readme-stats.vercel.app/api?username=byteD-x&show_icons=true&theme=transparent&hide_border=true&title_color=2563EB&text_color=52525B&icon_color=2563EB" width="49%" />
<img src="https://github-readme-stats.vercel.app/api/top-langs/?username=byteD-x&layout=compact&theme=transparent&hide_border=true&title_color=2563EB&text_color=52525B" width="49%" />

<br>

</div>

<br>

<p align="center">
  <code style="color: #A1A1AA;">systemctl status byteD-x --no-pager</code>
</p>
