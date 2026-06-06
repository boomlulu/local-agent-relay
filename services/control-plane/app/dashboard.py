from __future__ import annotations


def render_dashboard() -> str:
    return """
    <!doctype html>
    <html lang="zh-CN">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Local Agent Relay</title>
        <style>
          :root {
            --bg: #0a0e16;
            --bg-2: #0d1320;
            --card: #101826;
            --card-2: #0e1622;
            --line: #1d2a3d;
            --line-soft: #18243456;
            --ink: #e6edf6;
            --muted: #7c8aa3;
            --cyan: #22d3ee;
            --cyan-dim: #22d3ee33;
            --purple: #a855f7;
            --purple-dim: #a855f733;
            --ok: #34d399;
            --ok-soft: #34d39922;
            --amber: #f59e0b;
            --amber-soft: #f59e0b22;
            --danger: #f87171;
            --danger-soft: #f8717122;
            --gray: #64748b;
            --gray-soft: #64748b22;
            --mono: ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, Monaco, Consolas, monospace;
            --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
          }

          * { box-sizing: border-box; }

          body {
            margin: 0;
            font-family: var(--sans);
            color: var(--ink);
            background:
              radial-gradient(1100px 600px at 18% -8%, #14233a 0%, transparent 55%),
              radial-gradient(900px 520px at 92% 4%, #1c1235 0%, transparent 50%),
              linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%);
            background-attachment: fixed;
            min-height: 100vh;
          }

          .wrap {
            width: min(960px, calc(100% - 32px));
            margin: 0 auto;
          }

          /* ---------- top bar ---------- */
          header {
            position: sticky;
            top: 0;
            z-index: 20;
            backdrop-filter: blur(10px);
            background: linear-gradient(180deg, #0a0e16e6 0%, #0a0e1699 100%);
            border-bottom: 1px solid var(--line);
          }

          .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            padding: 14px 0;
          }

          .brand {
            display: flex;
            align-items: center;
            gap: 10px;
          }

          .brand .glyph {
            font-size: 20px;
            color: var(--cyan);
            text-shadow: 0 0 12px var(--cyan);
          }

          .brand .name {
            font-family: var(--mono);
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 2px;
            color: var(--ink);
          }

          .live {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-family: var(--mono);
            font-size: 11px;
            letter-spacing: 1.5px;
            color: var(--ok);
            padding: 3px 9px;
            border: 1px solid var(--ok-soft);
            border-radius: 999px;
            background: var(--ok-soft);
          }

          .live .dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--ok);
            box-shadow: 0 0 8px var(--ok);
            animation: pulse 1.8s ease-in-out infinite;
          }

          @keyframes pulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--ok); }
            50% { opacity: 0.35; box-shadow: 0 0 2px var(--ok); }
          }

          .links {
            display: flex;
            gap: 14px;
          }

          .links a {
            font-family: var(--mono);
            font-size: 12px;
            letter-spacing: 1px;
            color: var(--muted);
            text-decoration: none;
            transition: color 0.15s;
          }

          .links a:hover { color: var(--cyan); }

          main {
            display: grid;
            gap: 18px;
            padding: 22px 0 56px;
          }

          /* ---------- cards ---------- */
          .card {
            border: 1px solid var(--line);
            border-radius: 14px;
            background: linear-gradient(180deg, var(--card) 0%, var(--card-2) 100%);
            box-shadow:
              0 0 0 1px #0000,
              0 10px 30px -18px #000,
              inset 0 1px 0 0 #ffffff08;
          }

          .card.glow-cyan {
            border-color: #22d3ee2e;
            box-shadow: 0 0 28px -10px var(--cyan-dim), 0 10px 30px -18px #000, inset 0 1px 0 0 #ffffff0a;
          }

          .card-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding: 14px 18px;
            border-bottom: 1px solid var(--line-soft);
          }

          .card-head h2 {
            margin: 0;
            font-size: 13px;
            font-family: var(--mono);
            font-weight: 700;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: var(--muted);
          }

          .card-head .tag {
            font-family: var(--mono);
            font-size: 12px;
            color: var(--muted);
          }

          /* ---------- input card ---------- */
          form { display: grid; gap: 14px; padding: 18px; }

          textarea, input[type="text"], select {
            width: 100%;
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 13px 14px;
            color: var(--ink);
            background: #0a111c;
            font: inherit;
            transition: border-color 0.15s, box-shadow 0.15s;
          }

          textarea:focus, input[type="text"]:focus, select:focus {
            outline: none;
            border-color: var(--cyan);
            box-shadow: 0 0 0 3px var(--cyan-dim);
          }

          #instruction {
            min-height: 96px;
            resize: vertical;
            font-size: 16px;
            line-height: 1.5;
          }

          #instruction::placeholder { color: var(--muted); }

          .input-row {
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
          }

          .ghost-btn {
            appearance: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 9px 13px;
            background: #0b1320;
            color: var(--muted);
            font: inherit;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: border-color 0.15s, color 0.15s;
          }

          .ghost-btn:hover { border-color: var(--cyan); color: var(--cyan); }

          .primary {
            appearance: none;
            margin-left: auto;
            border: 1px solid var(--cyan);
            border-radius: 11px;
            padding: 11px 22px;
            background: linear-gradient(180deg, #22d3ee 0%, #0fb6d4 100%);
            color: #04141a;
            font: inherit;
            font-weight: 800;
            letter-spacing: 1px;
            cursor: pointer;
            box-shadow: 0 0 18px -4px var(--cyan-dim);
            transition: transform 0.08s, box-shadow 0.15s;
          }

          .primary:hover { box-shadow: 0 0 26px -2px var(--cyan); }
          .primary:active { transform: translateY(1px); }
          .primary:disabled { cursor: wait; opacity: 0.6; box-shadow: none; }

          /* image preview */
          #imagePreview {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 12px;
            border: 1px dashed var(--purple);
            border-radius: 12px;
            background: var(--purple-dim);
          }

          #imagePreview img {
            width: 52px;
            height: 52px;
            object-fit: cover;
            border-radius: 8px;
            border: 1px solid var(--purple);
          }

          #imageName {
            flex: 1;
            min-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-family: var(--mono);
            font-size: 12px;
            color: var(--purple);
          }

          .remove-x {
            appearance: none;
            border: 1px solid var(--purple);
            border-radius: 8px;
            width: 28px;
            height: 28px;
            background: transparent;
            color: var(--purple);
            cursor: pointer;
            font-size: 15px;
            line-height: 1;
          }

          .remove-x:hover { background: var(--purple); color: #fff; }

          /* advanced details */
          details.advanced {
            border-top: 1px solid var(--line-soft);
            margin: 2px -18px -18px;
            padding: 0;
          }

          details.advanced > summary {
            cursor: pointer;
            padding: 13px 18px;
            font-family: var(--mono);
            font-size: 12px;
            letter-spacing: 1px;
            color: var(--muted);
            list-style: none;
            user-select: none;
          }

          details.advanced > summary::-webkit-details-marker { display: none; }
          details.advanced > summary:hover { color: var(--purple); }
          details.advanced[open] > summary { color: var(--purple); }

          .advanced-body { display: grid; gap: 12px; padding: 0 18px 18px; }

          label.field {
            display: grid;
            gap: 6px;
            font-family: var(--mono);
            font-size: 11px;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: var(--muted);
          }

          /* ---------- focus card ---------- */
          .focus-body { padding: 18px; }

          .focus-top {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
          }

          .focus-title {
            margin: 12px 0 8px;
            font-size: 22px;
            line-height: 1.25;
            color: var(--ink);
          }

          .focus-message {
            margin: 0;
            color: var(--muted);
            font-size: 15px;
            line-height: 1.6;
          }

          .notify-badge {
            font-family: var(--mono);
            font-size: 12px;
            color: var(--cyan);
          }

          /* ---------- status chips ---------- */
          .chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            flex: 0 0 auto;
            border-radius: 999px;
            padding: 4px 11px;
            font-family: var(--mono);
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            border: 1px solid var(--gray-soft);
            background: var(--gray-soft);
            color: var(--gray);
          }

          .chip.completed { border-color: var(--ok-soft); background: var(--ok-soft); color: var(--ok); }
          .chip.created { border-color: var(--gray-soft); background: var(--gray-soft); color: var(--gray); }
          .chip.executing, .chip.validating, .chip.reporting, .chip.needs_user_input {
            border-color: var(--amber-soft); background: var(--amber-soft); color: var(--amber);
            animation: chip-pulse 1.6s ease-in-out infinite;
          }
          .chip.failed_execution, .chip.failed_validation, .chip.timeout, .chip.cancelled {
            border-color: var(--danger-soft); background: var(--danger-soft); color: var(--danger);
          }

          @keyframes chip-pulse {
            0%, 100% { box-shadow: 0 0 0 0 var(--amber-soft); }
            50% { box-shadow: 0 0 0 4px #f59e0b14; }
          }

          /* ---------- detail card ---------- */
          .detail-body { padding: 18px; }

          .empty {
            padding: 34px 18px;
            color: var(--muted);
            text-align: center;
            font-size: 14px;
          }

          .section-title {
            margin: 20px 0 10px;
            font-family: var(--mono);
            font-size: 12px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: var(--cyan);
          }
          .section-title:first-child { margin-top: 0; }

          .info-list { display: grid; gap: 0; margin: 0; }

          .info-row {
            display: grid;
            grid-template-columns: 130px minmax(0, 1fr);
            gap: 14px;
            padding: 10px 0;
            border-bottom: 1px solid var(--line-soft);
          }

          .info-row strong {
            font-family: var(--mono);
            color: var(--muted);
            font-size: 12px;
            font-weight: 600;
          }

          .info-row span { overflow-wrap: anywhere; color: var(--ink); }
          .info-row span.mono { font-family: var(--mono); font-size: 13px; }

          .pill-row { display: flex; flex-wrap: wrap; gap: 8px; }

          .vchip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            border-radius: 10px;
            padding: 7px 11px;
            font-size: 13px;
            border: 1px solid var(--line);
            background: #0a111c;
          }
          .vchip.passed { border-color: var(--ok-soft); }
          .vchip.failed { border-color: var(--danger-soft); }
          .vchip.skipped { border-color: var(--gray-soft); }
          .vchip .vname { font-weight: 650; color: var(--ink); }
          .vchip .vmeta { font-family: var(--mono); font-size: 11px; color: var(--muted); }

          .has-image {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            color: var(--purple);
            margin-top: 6px;
          }

          pre {
            margin: 0;
            overflow: auto;
            max-height: 480px;
            border-radius: 12px;
            padding: 14px;
            border: 1px solid var(--line);
            background: #060a12;
            color: #cbd5e1;
            font-family: var(--mono);
            font-size: 12.5px;
            line-height: 1.6;
            white-space: pre-wrap;
          }

          details.fold {
            margin-top: 14px;
            border: 1px solid var(--line);
            border-radius: 12px;
            background: #0a111c;
          }

          details.fold > summary {
            cursor: pointer;
            padding: 12px 14px;
            font-family: var(--mono);
            font-size: 12px;
            letter-spacing: 1px;
            color: var(--muted);
            list-style: none;
            user-select: none;
          }
          details.fold > summary::-webkit-details-marker { display: none; }
          details.fold > summary:hover { color: var(--cyan); }
          details.fold[open] > summary { color: var(--cyan); border-bottom: 1px solid var(--line-soft); }
          details.fold .fold-body { padding: 14px; }

          /* ---------- task list ---------- */
          .task-list { display: grid; gap: 8px; padding: 14px; }

          .task {
            width: 100%;
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 12px 13px;
            background: #0a111c;
            text-align: left;
            cursor: pointer;
            transition: border-color 0.15s, background 0.15s;
          }

          .task:hover { border-color: #22d3ee55; }

          .task.active {
            border-color: var(--cyan);
            background: #0c1722;
            box-shadow: inset 0 0 0 1px var(--cyan-dim);
          }

          .task-line {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
          }

          .task-line .t-title {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            color: var(--ink);
            font-weight: 650;
          }

          .task-meta {
            margin-top: 6px;
            font-family: var(--mono);
            font-size: 11px;
            color: var(--muted);
          }

          .error-line {
            margin: 0 18px 16px;
            color: var(--danger);
            font-size: 13px;
          }

          [hidden] { display: none !important; }

          @media (max-width: 720px) {
            .info-row { grid-template-columns: 1fr; gap: 3px; }
            .primary { margin-left: 0; width: 100%; }
          }
        </style>
      </head>
      <body>
        <header>
          <div class="wrap topbar">
            <div class="brand">
              <span class="glyph">&#x2B21;</span>
              <span class="name">LOCAL AGENT RELAY</span>
              <span class="live"><span class="dot"></span>LIVE</span>
            </div>
            <nav class="links">
              <a href="/docs">API</a>
              <a href="/health">HEALTH</a>
            </nav>
          </div>
        </header>

        <main class="wrap">
          <!-- input card -->
          <section class="card glow-cyan">
            <div class="card-head">
              <h2>// 新建任务</h2>
              <span class="tag">输入指令</span>
            </div>
            <form id="taskForm">
              <input type="hidden" id="title">
              <textarea id="instruction" placeholder="想让 Agent 做什么？例如：告诉我现在几点了" required>告诉我现在几点了</textarea>

              <div id="imagePreview" hidden>
                <img id="imageThumb" alt="预览">
                <span id="imageName"></span>
                <button type="button" class="remove-x" id="imageRemove" title="移除">&times;</button>
              </div>

              <div class="input-row">
                <button type="button" class="ghost-btn" id="imageButton">&#x2295; 图片</button>
                <input type="file" id="imageInput" accept="image/*" hidden>
                <button id="submitButton" class="primary" type="submit">创 建 &#x25B8;</button>
              </div>

              <details class="advanced">
                <summary>&#x2699; 高级</summary>
                <div class="advanced-body">
                  <label class="field">
                    Executor
                    <select id="executor">
                      <option value="gemma" selected>Gemma 本地助手</option>
                      <option value="shell">shell</option>
                    </select>
                  </label>
                  <label class="field">
                    验收管线
                    <select id="pipeline">
                      <option value="">不验收（仅执行）</option>
                    </select>
                  </label>
                  <label class="field" id="shellSettings" hidden>
                    Shell Command
                    <textarea id="command">echo task:$LOCAL_AGENT_RELAY_TASK_ID && echo instruction:$LOCAL_AGENT_RELAY_INSTRUCTION</textarea>
                  </label>
                </div>
              </details>
            </form>
            <div id="formError" class="error-line" hidden></div>
          </section>

          <!-- focus card -->
          <section class="card" id="focusPanel">
            <div class="card-head">
              <h2>// 现在关注</h2>
              <span class="tag" id="focusNotify" hidden><span class="notify-badge">&#x1F50A; 已通知</span></span>
            </div>
            <div class="focus-body">
              <div class="focus-top">
                <span id="focusStatus" class="chip">加载中</span>
              </div>
              <h3 id="focusTitle" class="focus-title">正在读取任务</h3>
              <p id="focusMessage" class="focus-message">稍等，正在同步控制平面状态。</p>
            </div>
          </section>

          <!-- detail card -->
          <section class="card">
            <div class="card-head">
              <h2>// 任务详情</h2>
              <span class="tag" id="selectedTaskLabel">未选择</span>
            </div>
            <div id="taskDetail" class="detail-body">
              <div class="empty">选择任务后，这里显示结果、验收与报告；执行日志默认折叠。</div>
            </div>
          </section>

          <!-- recent tasks -->
          <section class="card">
            <div class="card-head">
              <h2>// 最近任务</h2>
              <span class="tag" id="taskCount">加载中</span>
            </div>
            <div id="taskList" class="task-list"></div>
          </section>
        </main>

        <script>
          const state = {
            selectedTaskId: null,
            tasks: [],
            pollTimer: null,
            imageDataUrl: null,
          };

          const taskList = document.querySelector("#taskList");
          const taskDetail = document.querySelector("#taskDetail");
          const taskCount = document.querySelector("#taskCount");
          const selectedTaskLabel = document.querySelector("#selectedTaskLabel");
          const form = document.querySelector("#taskForm");
          const formError = document.querySelector("#formError");
          const submitButton = document.querySelector("#submitButton");
          const focusStatus = document.querySelector("#focusStatus");
          const focusTitle = document.querySelector("#focusTitle");
          const focusMessage = document.querySelector("#focusMessage");
          const focusNotify = document.querySelector("#focusNotify");
          const executorSelect = document.querySelector("#executor");
          const shellSettings = document.querySelector("#shellSettings");
          const pipelineSelect = document.querySelector("#pipeline");
          const instructionInput = document.querySelector("#instruction");
          const imageButton = document.querySelector("#imageButton");
          const imageInput = document.querySelector("#imageInput");
          const imagePreview = document.querySelector("#imagePreview");
          const imageThumb = document.querySelector("#imageThumb");
          const imageName = document.querySelector("#imageName");
          const imageRemove = document.querySelector("#imageRemove");

          function escapeHtml(value) {
            return String(value ?? "")
              .replaceAll("&", "&amp;")
              .replaceAll("<", "&lt;")
              .replaceAll(">", "&gt;")
              .replaceAll('"', "&quot;")
              .replaceAll("'", "&#039;");
          }

          function statusClass(status) {
            return `chip ${status}`;
          }

          function statusLabel(status) {
            const labels = {
              created: "等待执行",
              executing: "正在执行",
              validating: "正在验收",
              reporting: "正在总结",
              completed: "已完成",
              failed_execution: "执行失败",
              failed_validation: "验收失败",
              needs_user_input: "需要确认",
              timeout: "已超时",
              cancelled: "已取消",
            };
            return labels[status] || status;
          }

          function formatTime(value) {
            if (!value) return "-";
            const date = new Date(value);
            if (Number.isNaN(date.getTime())) return value;
            return date.toLocaleString("zh-CN", {hour12: false});
          }

          function taskPriority(task) {
            const priority = {
              failed_execution: 0,
              failed_validation: 0,
              needs_user_input: 0,
              timeout: 0,
              executing: 1,
              validating: 1,
              reporting: 1,
              created: 2,
              completed: 3,
              cancelled: 4,
            };
            return priority[task.status] ?? 9;
          }

          function pickFocusTask(tasks) {
            if (state.selectedTaskId) {
              const selected = tasks.find((task) => task.id === state.selectedTaskId);
              if (selected && selected.status !== "completed") return selected;
            }
            return [...tasks].sort((a, b) => {
              const priorityDelta = taskPriority(a) - taskPriority(b);
              if (priorityDelta !== 0) return priorityDelta;
              return new Date(b.created_at) - new Date(a.created_at);
            })[0];
          }

          function focusCopy(task) {
            if (!task) {
              return {
                title: "还没有任务",
                message: "先创建一个任务。之后这里会优先显示失败、正在执行或刚完成的任务。",
              };
            }
            if (["failed_execution", "failed_validation", "timeout"].includes(task.status)) {
              return {
                title: task.title,
                message: task.error || "这个任务需要你关注。展开详情可以查看执行日志和失败原因。",
              };
            }
            if (["executing", "validating", "reporting", "created"].includes(task.status)) {
              return {
                title: task.title,
                message: "任务还在进行中。页面会自动刷新，完成或失败后这里会更新。",
              };
            }
            if (task.status === "completed") {
              return {
                title: task.title,
                message: task.summary || "最近任务已完成。需要排查时可以展开详情里的执行日志。",
              };
            }
            return {
              title: task.title,
              message: task.summary || "任务状态已更新。",
            };
          }

          async function fetchJson(url, options) {
            const response = await fetch(url, options);
            if (!response.ok) {
              const body = await response.text();
              throw new Error(`${response.status} ${response.statusText}: ${body}`);
            }
            return response.json();
          }

          function renderFocus(tasks) {
            const task = pickFocusTask(tasks);
            const copy = focusCopy(task);
            focusTitle.textContent = copy.title;
            focusMessage.textContent = copy.message;
            focusStatus.className = statusClass(task ? task.status : "");
            focusStatus.textContent = task ? statusLabel(task.status) : "空闲";
            if (task && !state.selectedTaskId) {
              state.selectedTaskId = task.id;
            }
          }

          async function loadPipelines() {
            try {
              const pipelines = await fetchJson("/pipelines");
              const current = pipelineSelect.value;
              pipelineSelect.innerHTML = `<option value="">不验收（仅执行）</option>` + pipelines.map((p) =>
                `<option value="${escapeHtml(p.pipeline_name)}">${escapeHtml(p.pipeline_name)} — ${escapeHtml(p.project_type)} · ${p.validators} 验收</option>`
              ).join("");
              pipelineSelect.value = current;
            } catch (error) {
              console.error(error);
            }
          }

          async function loadTasks() {
            const tasks = await fetchJson("/tasks");
            state.tasks = tasks;
            taskCount.textContent = `${tasks.length} 个`;
            renderFocus(tasks);

            taskList.innerHTML = tasks.length ? tasks.map((task) => `
              <button class="task ${task.id === state.selectedTaskId ? "active" : ""}" data-task-id="${task.id}" type="button">
                <div class="task-line">
                  <span class="t-title">${escapeHtml(task.title)}</span>
                  <span class="${statusClass(task.status)}">${escapeHtml(statusLabel(task.status))}</span>
                </div>
                <div class="task-meta">${escapeHtml(formatTime(task.finished_at || task.started_at || task.created_at))}</div>
              </button>
            `).join("") : `<div class="empty">暂无任务。</div>`;

            if (!state.selectedTaskId && tasks.length > 0) {
              state.selectedTaskId = tasks[0].id;
            }
            if (state.selectedTaskId) {
              await loadTaskDetail(state.selectedTaskId);
            }
          }

          function validationIcon(status) {
            if (status === "passed") return "✅";
            if (status === "failed") return "❌";
            return "⏭️";
          }
          function renderValidations(items) {
            if (!items || !items.length) return "";
            const rows = items.map((v) =>
              `<div class="vchip ${escapeHtml(v.status)}">${validationIcon(v.status)} <span class="vname">${escapeHtml(v.name)}</span> <span class="vmeta">${escapeHtml(v.adapter)} · ${escapeHtml(v.detail || v.status)}</span></div>`
            ).join("");
            return `<h3 class="section-title">验收结果</h3><div class="pill-row">${rows}</div>`;
          }
          function renderReport(report) {
            if (!report) return "";
            return `<h3 class="section-title">执行报告</h3><pre>${escapeHtml(report)}</pre>`;
          }

          async function loadTaskDetail(taskId) {
            const task = await fetchJson(`/tasks/${taskId}`);
            state.selectedTaskId = task.id;
            selectedTaskLabel.textContent = task.title;

            const notified = (task.logs || []).some((log) => log.stream === "notify");
            focusNotify.hidden = !(notified && task.status === "completed");

            const logs = (task.logs || []).map((log) => {
              return `[${formatTime(log.created_at)}] ${log.stream}\\n${log.message}`;
            }).join("\\n\\n");

            const imageRow = task.image_path
              ? `<div class="has-image">🖼 含图片输入</div>`
              : "";

            taskDetail.innerHTML = `
              <h3 class="section-title">概要</h3>
              <div class="info-list">
                <div class="info-row"><strong>状态</strong><span>${escapeHtml(statusLabel(task.status))}</span></div>
                <div class="info-row"><strong>结果 / 答案</strong><span>${escapeHtml(task.summary || task.error || "等待结果")}</span></div>
                <div class="info-row"><strong>指令</strong><span>${escapeHtml(task.instruction)}</span></div>
              </div>
              ${imageRow}
              ${renderValidations(task.validations)}
              ${renderReport(task.report)}
              <details class="fold">
                <summary>执行日志</summary>
                <div class="fold-body">
                  <pre>${escapeHtml(logs || "暂无日志")}</pre>
                </div>
              </details>
              <details class="fold">
                <summary>技术信息</summary>
                <div class="fold-body">
                  <div class="info-list">
                    <div class="info-row"><strong>Executor</strong><span class="mono">${escapeHtml(task.executor)}</span></div>
                    <div class="info-row"><strong>Exit Code</strong><span class="mono">${escapeHtml(task.exit_code ?? "-")}</span></div>
                    <div class="info-row"><strong>Task ID</strong><span class="mono">${escapeHtml(task.id)}</span></div>
                    <div class="info-row"><strong>Command</strong><span class="mono">${escapeHtml(task.command || "-")}</span></div>
                  </div>
                </div>
              </details>
            `;
          }

          taskList.addEventListener("click", async (event) => {
            const button = event.target.closest("[data-task-id]");
            if (!button) return;
            state.selectedTaskId = button.dataset.taskId;
            await loadTasks();
          });

          imageButton.addEventListener("click", () => imageInput.click());

          imageInput.addEventListener("change", () => {
            const file = imageInput.files && imageInput.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = () => {
              state.imageDataUrl = reader.result;
              imageThumb.src = reader.result;
              imageName.textContent = file.name;
              imagePreview.hidden = false;
            };
            reader.readAsDataURL(file);
          });

          function clearImage() {
            state.imageDataUrl = null;
            imageInput.value = "";
            imageThumb.removeAttribute("src");
            imageName.textContent = "";
            imagePreview.hidden = true;
          }

          imageRemove.addEventListener("click", clearImage);

          form.addEventListener("submit", async (event) => {
            event.preventDefault();
            formError.hidden = true;
            submitButton.disabled = true;
            try {
              const instruction = instructionInput.value;
              const autoTitle = instruction.replace(/\\s+/g, " ").trim().slice(0, 40) || "任务";
              const payload = {
                title: autoTitle,
                instruction: instruction,
                executor: executorSelect.value,
              };
              if (payload.executor === "shell") {
                payload.command = document.querySelector("#command").value;
              }
              if (pipelineSelect.value) {
                payload.pipeline = pipelineSelect.value;
              }
              if (state.imageDataUrl) {
                payload.image_base64 = state.imageDataUrl;
              }
              const task = await fetchJson("/tasks", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payload),
              });
              state.selectedTaskId = task.id;
              clearImage();
              await loadTasks();
            } catch (error) {
              formError.textContent = error.message;
              formError.hidden = false;
            } finally {
              submitButton.disabled = false;
            }
          });

          async function refresh() {
            await loadTasks();
          }

          executorSelect.addEventListener("change", () => {
            shellSettings.hidden = executorSelect.value !== "shell";
          });

          async function startPolling() {
            await loadPipelines();
            await loadTasks();
            state.pollTimer = window.setInterval(() => {
              loadTasks().catch(console.error);
            }, 2500);
          }

          startPolling().catch((error) => {
            focusTitle.textContent = "状态读取失败";
            focusMessage.textContent = error.message;
            focusStatus.className = "chip failed_execution";
            focusStatus.textContent = "离线";
            taskList.innerHTML = `<div class="empty">${escapeHtml(error.message)}</div>`;
          });
        </script>
      </body>
    </html>
    """
