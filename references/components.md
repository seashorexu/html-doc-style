# 组件结构与用法

生成页面时按本文件的 class 结构填写。所有组件样式已定义在 `assets/doc-style.css`，**不要重写样式，只套结构**。
需要看真实渲染效果时打开 `assets/style-guide.html`（它自身就是用这套规范排的）。

---

## 0. 页面骨架总览

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>文档标题</title>
<style>/* 内联 assets/doc-style.css 的全部内容 */</style>
</head>
<body>
<header class="hero">…</header>
<div class="layout">
  <nav class="toc" id="toc">…</nav>
  <main>
    <section id="…">…</section>
    …
  </main>
</div>
<footer>…</footer>
<script>/* 复制按钮 + 目录高亮，见本文最后一节，必须保留 */</script>
</body>
</html>
```

`assets/template.html` 是填好占位的完整骨架，优先复制它再替换文字。

---

## 1. 页首 `.hero`

```html
<header class="hero">
  <div class="kicker">分类 · 眉题</div>
  <h1>文档主标题</h1>
  <p class="lead">一到两句话说明这份文档解决什么、给谁读、按什么顺序组织。</p>
  <div class="meta">
    <span class="chip">日期 <b>2026-11-10</b></span>
    <span class="chip">版本 <b>v1.0</b></span>
  </div>
</header>
```

- `.kicker` 11.5px、2px 字距、大写、主色，只作眉题。
- `.lead` 15px、`--muted`、限宽 760px，**不要写成长段落**。
- `.chip` 只放不参与阅读流的元数据；`<b>` 让值比标签重一档。
- 长标题可在 `h1` 里用 `<br>` 手动断行，控制在两行内。

## 2. 目录 `.toc`

```html
<nav class="toc" id="toc">
  <h3>目录</h3>
  <a href="#overview"><span class="num">00</span>一页速查</a>
  <a href="#content"><span class="num">01</span>正文与代码</a>
</nav>
```

- `href` 的锚点必须与 `<section id>` **一一对应**，编号用两位数字（00–11）。
- 目录项文字控制在 6–10 字，过长会在 216px 列里折行。
- 当前章高亮由底部脚本的 `IntersectionObserver` 负责，不要手写 `class="active"`（仅首个可预置）。

## 3. 章节头 `section`

```html
<section id="content">
  <h2><span class="idx">01</span>正文与代码</h2>
  <p class="sec-lead">一句话说明本章解决什么。</p>
  …
</section>
```

- **每章都用同一个三段式结构重复**，秩序感来自可预期，不要给某章加分割线或换布局。
- `.idx` 编号与目录 `.num` 保持一致。
- 章内分节用 `h3`（上留白 28px），再下一层用 `h4`。

## 4. 卡片 `.cards` / `.card` / `.badge`

```html
<div class="cards">
  <div class="card">
    <span class="badge">A · 一次性</span>
    <h4>卡片标题</h4>
    <p>说明文字，12.5px 次要灰。</p>
  </div>
  <div class="card">
    <span class="badge b">B · 每次</span>
    <h4>卡片标题</h4>
    <p>…</p>
  </div>
  <div class="card">
    <span class="badge c">C · 日常</span>
    <h4>卡片标题</h4>
    <p>…</p>
  </div>
</div>
```

- 三列适合「并列选项 / 三个层次 / 三个阶段」；只有一段内容时去掉 `.cards`，直接用单个 `.card`。
- 徽标顺序固定 `.badge` → `.badge.b` → `.badge.c`。
- 卡片内**不再嵌套卡片或表格**；需要表格就与卡片平级另起。

## 5. 提示 / 引用 `.callout`

```html
<div class="callout ok">
  <span class="ttl">结论 / 记住这一行就够</span>
  <p>最希望读者记住的一句话。</p>
</div>
```

四态与语义固定绑定，**不要混用**：

| class | 语义 | 典型用途 |
|---|---|---|
| `.callout.note` | 中性说明 / 引文 | 补充背景、引用原文、不影响操作的注释 |
| `.callout.ok` | 结论 / 推荐做法 | 「记住这一行就够」、当前默认配置 |
| `.callout.warn` | 注意 / 容易踩的坑 | 需要留意但不至于失败的边界条件 |
| `.callout.danger` | 危险 / 不可逆 | 会丢数据、装错包、必须停手 |

- `.ttl` 必须有；`<p>` 可多个，最后一个自动去掉下边距。
- **不使用 `<blockquote>`**：原稿把引用统一归到 `.callout`，避免维护第二套样式。
- 提示块里可以放 `code`；不要放代码块、表格或步骤。

## 6. 行内代码 `code`

```html
双击 <code>start_after_reboot.cmd</code>；参数 <code>-ngl 99</code>。
```

- 用于文件名、参数、命令碎片、类名、短变量名。
- 暖灰底棕字，4px 圆角，**与深色代码块刻意区分**：读者要能一眼分辨「一个词」和「一段命令」。
- 表格内的 `code` 会自动换行断词，长路径也不会撑破表格。

## 7. 代码块 `.codewrap > pre`

```html
<div class="codewrap">
  <pre><code><span class="cmt"># 注释</span>
<span class="key">llama serve</span> -m <span class="str">"model.gguf"</span> -c <span class="str">8192</span></code></pre>
</div>
```

- 语法只上三色：`.cmt` 注释灰蓝、`.key` 关键字 / 参数薄荷、`.str` 字符串 / 数值沙金。**不做完整语法高亮**。
- 右上角「复制」按钮由底部脚本自动注入，**不要手写按钮**；前提是 `pre` 必须直接包在 `.codewrap` 里。
- **Windows 命令给一整行可复制文本**，不要用 `\` 分行续行（PowerShell 不认），长命令宁可横向滚动。
- `pre` 内的 `<` `>` 必须写成 `&lt;` `&gt;`；展示 HTML 结构时尤其注意。
- 打印时自动反相为浅底，不需要额外处理。

## 8. 表格 `table`

```html
<table>
  <thead><tr><th style="width:28%">项目</th><th style="width:20%">数值</th><th>说明</th></tr></thead>
  <tbody>
    <tr><td>上下文</td><td class="num">8192</td><td>状态 <span class="yes">正常</span></td></tr>
    <tr><td>纯黑背景</td><td class="num">—</td><td><span class="no">禁止</span></td></tr>
  </tbody>
</table>
```

- **无竖线**，只有横向 `--line2` 分隔线；最后一行自动去底线。
- 表头 11.5px 浅米底；表格文字 12.5px；单元内边距 10×12。
- 数字 / 版本 / 端口列加 `.num` 用等宽字；是 / 否用 `.yes`（主色）/ `.no`（砖红）。
- 用 `style="width:…"` 控制列宽是可以接受的（布局值，非视觉色值）。
- 表格整体 `break-inside:avoid`，不要手动拆成两张表来规避分页。

## 9. 步骤 `.steps`

```html
<ol class="steps">
  <li><h4>第一步</h4><p>序号由 CSS 计数器自动生成。</p></li>
  <li><h4>第二步</h4><p>竖线自动串联。</p></li>
  <li><h4>第三步</h4><p>最后一项自动去掉竖线。</p></li>
</ol>
```

- 用 `<ol class="steps">`，序号**不要手写**（`counter-reset` / `counter-increment` 自动编号）。
- 每步只放一个 `h4` + 一段 `p`，不放代码块或表格。

## 10. 其他

| 组件 | 结构 | 用途 |
|---|---|---|
| 文件清单 | `<div class="card filelist"><p><code>名</code>　—　说明</p>…</div>` | 路径长时 `code` 自动断词 |
| 分隔 | `<hr>` | 章节内大转折，34px 上下留白，慎用 |
| 页脚 | `<footer>` | 版本 / 来源 / 一句话备注，打印时隐藏 |
| 状态词 | `<span class="yes">` / `<span class="no">` | 表格或正文中的通过与禁止 |

---

## 11. 底部脚本（必须保留）

复制 `assets/template.html` 的 `<script>` 区块，或直接用以下片段。它负责两件事：给每个 `.codewrap` 内的 `pre` 注入复制按钮、让目录随滚动高亮。缺少它，代码块将没有复制按钮。

```javascript
"use strict";
document.querySelectorAll("pre").forEach(pre => {
  const btn = document.createElement("button");
  btn.className = "copy";
  btn.type = "button";
  btn.textContent = "复制";
  btn.addEventListener("click", async () => {
    const text = pre.innerText;
    let ok = false;
    try { await navigator.clipboard.writeText(text); ok = true; }
    catch (e) {
      const ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { ok = document.execCommand("copy"); } catch (_) {}
      ta.remove();
    }
    btn.textContent = ok ? "已复制" : "复制失败";
    setTimeout(() => { btn.textContent = "复制"; }, 1400);
  });
  const wrap = pre.parentElement;
  if (wrap && wrap.classList.contains("codewrap")) wrap.appendChild(btn);
});
const links = [...document.querySelectorAll(".toc a")];
const byId = new Map(links.map(a => [a.getAttribute("href").slice(1), a]));
if ("IntersectionObserver" in window) {
  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      links.forEach(a => a.classList.remove("active"));
      const a = byId.get(entry.target.id);
      if (a) a.classList.add("active");
    });
  }, { rootMargin: "-10% 0px -75% 0px", threshold: 0 });
  document.querySelectorAll("main section").forEach(s => io.observe(s));
}
if (byId.size) byId.get(byId.keys().next().value).classList.add("active");
```

> 最后一行按目录第一项预置高亮；若首节 id 固定，也可写成 `byId.get("overview")`。

---

## 12. 交付前检查清单

- [ ] 目录每个 `href="#…"` 都有对应的 `<section id="…">`，反之亦然
- [ ] 所有 `pre` 都直接包在 `.codewrap` 里
- [ ] `.callout` 四态都带 `.ttl`
- [ ] 命令示例是一整行，没有 `\` 续行
- [ ] 没有外部字体 / 图片 / CDN 引用
- [ ] 页面里没有散落的十六进制色值或额外字号
- [ ] 含 `@media print` 与 920px 响应式规则
- [ ] 底部脚本已保留
- [ ] 运行 `scripts/validate_html.py <输出文件>` 通过
