# 承太郎 · 知识宫殿博客

一个静态个人博客，展示 Obsidian vault 里的全部笔记。

- **线上地址**：https://mysterio-jzp.github.io/knowledge-palace/
- **部署方式**：GitHub Pages（仓库 `mysterio-jzp/knowledge-palace`，源分支 `main` 根目录）
- **架构**：单页应用 `index.html` + 索引 `notes.json` + 真实笔记 `notes/N.md`
- **分类**：完全由 vault 真实目录自动生成（顶部 tab = 一级目录名），不写死

---

## 目录结构

```
blog-dist/                # 部署源（与 vault 根目录同级，即 <vault>/blog-dist）
├── index.html            # 应用外壳（CSS + JS，数据驱动渲染）
├── notes.json            # 索引：每篇的 id/room(分类)/path(真实路径)/title/tags/...
├── .nojekyll             # 禁用 Jekyll，让 .md 原样 serve（必须保留！）
├── notes/
│   ├── 0.md             # 第 0 篇（内容 = vault 里对应 .md 的副本）
│   ├── 1.md
│   └── ...
├── tools/
│   ├── regen.py          # 从 vault 真实路径重建 notes.json + notes/*.md
│   └── deploy.py         # 把 blog-dist/ 推送到 GitHub 并触发 Pages 重建
└── README.md             # 本文件
```

> vault 根目录（`blog-dist` 的父目录）下即你的 Obsidian 笔记：
> `Agent/`、`人工智能基础/`、`线性代数/`、`网络工程/`、`学习计划.md` 等。

---

## 怎么添加一篇新笔记

### 方法 A：本地一键（推荐，最省事）

前提：本机装了 Python 3，且笔记已写进 vault 对应目录。

**1) 在 vault 里新建笔记**

放到对应的一级目录即可，例如要归类到「Agent」就放 `Agent/你的笔记.md`。
笔记顶部建议带 YAML frontmatter（博客会读取 `title` / `date` / `tags` 展示）：

```markdown
---
title: "你的笔记标题"
date: 2026-08-04
tags: [Agent, 缓存]
aliases: []
---

正文从这里开始……
```

> 不设 `title` 时会自动用文件名当标题；不设 `tags` 也没关系。

**2) 重建索引和笔记副本**

```bash
cd <vault>/blog-dist
python3 tools/regen.py
```

脚本会扫描 vault 全部 `.md`，重新生成 `notes.json` 并把每篇复制到 `notes/N.md`。
新增的笔记会自动获得下一个编号，分类 tab 也会按真实目录自动更新。

**3) 部署上线**

```bash
cd <vault>/blog-dist
GH_TOKEN=ghp_你的GitHubToken python3 tools/deploy.py
```

- `GH_TOKEN` 是你的 GitHub Personal Access Token（需 `repo` 权限）。**不要写进文件**。
- 脚本会把 `index.html` / `notes.json` / `notes/*.md` / `tools/*.py` / `README.md` 全部推到仓库并触发 Pages 重建。
- 部署完成后，浏览器对博客页**硬刷新（Cmd+Shift+R）**即可看到新笔记。

---

### 方法 B：GitHub 网页手动（不依赖本地 Python）

适合临时加一篇、或不在本机时。

**1) 上传笔记正文**

进仓库 `notes/` 目录 → `Add file` → `Create new file`，文件名用**当前最大编号 +1**（如现有 `0.md`~`40.md`，新文件就叫 `41.md`），内容粘贴你的 Markdown 正文，提交。

**2) 在索引里登记这一篇**

打开仓库根目录的 `notes.json`，在数组末尾加一条（注意前面那条末尾要有逗号）：

```json
 {
  "id": 41,
  "room": "Agent",
  "path": "Agent/你的笔记.md",
  "date": "2026-08-04",
  "title": "你的笔记标题",
  "tags": ["Agent"],
  "from": "你的笔记",
  "summary": "一句话摘要……",
  "file": "notes/41.md"
 }
```

- `id` / `file` 的编号要和第一步的文件名一致。
- `room` 填真实一级目录名（会显示在分类 tab 和面包屑）。
- `summary` 留短一点，是卡片上的预览文字。

提交后等 1 分钟左右 Pages 重建，硬刷新即可。

---

## 注意事项

- **`.nojekyll` 不能删**：删了 GitHub Pages 会启用 Jekyll，把带 frontmatter 的 `.md` 编译成 `.html`，导致 `notes/N.md` 路径 404、文章打不开（页面会显示「此卷暂不可读」）。
- **分类自动生成**：你在 vault 里新建一个一级目录，博客顶部分类 tab 会自动多出来；删光某目录的笔记，对应 tab 也会消失。无需改任何代码。
- **改笔记内容**：直接改 vault 里的源 `.md`，然后跑方法 A 的 `regen.py` + `deploy.py` 重新发布即可。也可以在 GitHub 网页直接编辑 `notes/N.md`（但这不会同步回你的 Obsidian vault）。
- **缓存**：`index.html` / `notes.json` 更新后，浏览器可能需要硬刷新才能拿到新版；笔记正文 `.md` 已设 `no-store`，普通刷新即可。

## 当前数据（生成时快照）

| 分类（= vault 一级目录） | 篇数 |
|---|---|
| Agent | 29 |
| 人工智能基础 | 7 |
| 线性代数 | 3 |
| 网络工程 | 1 |
| 其他（顶层散落文件） | 1 |
| **合计** | **41** |
