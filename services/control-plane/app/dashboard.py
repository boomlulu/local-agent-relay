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
            --ink: #1f2328;
            --muted: #667085;
            --line: #d0d7de;
            --soft: #f6f8fa;
            --accent: #0f766e;
            --accent-soft: #f0fdfa;
            --danger: #b42318;
            --danger-soft: #fee4e2;
            --ok: #166534;
            --ok-soft: #dcfce7;
            --warn: #92400e;
            --warn-soft: #fef3c7;
            --code: #0f172a;
          }

          * {
            box-sizing: border-box;
          }

          body {
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            color: var(--ink);
            background: #ffffff;
          }

          header {
            border-bottom: 1px solid var(--line);
            background: #f8fbfa;
          }

          .wrap {
            width: min(1180px, calc(100% - 32px));
            margin: 0 auto;
          }

          .hero {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 20px;
            padding: 22px 0 18px;
          }

          h1 {
            margin: 0 0 6px;
            font-size: 32px;
            line-height: 1.1;
            letter-spacing: 0;
          }

          p {
            margin: 0;
            color: var(--muted);
            line-height: 1.55;
          }

          .actions {
            display: flex;
            gap: 10px;
            align-items: center;
          }

          a.button,
          button {
            appearance: none;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 9px 12px;
            background: #ffffff;
            color: var(--ink);
            cursor: pointer;
            font: inherit;
            font-weight: 650;
            text-decoration: none;
          }

          button.primary {
            border-color: var(--accent);
            background: var(--accent);
            color: #ffffff;
          }

          button:disabled {
            cursor: wait;
            opacity: 0.65;
          }

          main {
            display: grid;
            grid-template-columns: minmax(0, 1.35fr) 360px;
            gap: 18px;
            padding: 22px 0 44px;
          }

          section {
            min-width: 0;
          }

          .panel,
          .focus {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: #ffffff;
          }

          .focus {
            grid-column: 1 / -1;
            padding: 18px;
            background: linear-gradient(180deg, #f8fbfa 0%, #ffffff 100%);
          }

          .focus-head,
          .panel-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
          }

          .panel-head {
            padding: 14px 16px;
            border-bottom: 1px solid var(--line);
          }

          h2 {
            margin: 0;
            font-size: 18px;
            letter-spacing: 0;
          }

          .focus-title {
            margin: 10px 0 6px;
            font-size: 26px;
            line-height: 1.2;
            letter-spacing: 0;
          }

          .focus-message {
            max-width: 860px;
            color: var(--ink);
            font-size: 17px;
          }

          .focus-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 16px;
          }

          .status {
            flex: 0 0 auto;
            border-radius: 999px;
            padding: 4px 10px;
            background: var(--soft);
            color: var(--muted);
            font-size: 12px;
            font-weight: 750;
          }

          .status.completed {
            background: var(--ok-soft);
            color: var(--ok);
          }

          .status.executing,
          .status.created {
            background: var(--warn-soft);
            color: var(--warn);
          }

          .status.failed_execution,
          .status.failed_validation,
          .status.timeout {
            background: var(--danger-soft);
            color: var(--danger);
          }

          form {
            display: grid;
            gap: 12px;
            padding: 16px;
          }

          label {
            display: grid;
            gap: 6px;
            color: var(--muted);
            font-size: 13px;
            font-weight: 650;
          }

          input,
          textarea,
          select {
            width: 100%;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 10px 11px;
            color: var(--ink);
            background: #ffffff;
            font: inherit;
          }

          textarea {
            min-height: 86px;
            resize: vertical;
          }

          details {
            border-top: 1px solid var(--line);
          }

          details > summary {
            cursor: pointer;
            padding: 12px 16px;
            color: var(--muted);
            font-weight: 700;
            list-style-position: inside;
          }

          details .details-body {
            padding: 0 16px 16px;
          }

          [hidden] {
            display: none !important;
          }

          .task-list {
            display: grid;
            gap: 8px;
            padding: 12px;
          }

          .task {
            width: 100%;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 11px;
            background: #ffffff;
            text-align: left;
          }

          .task.active {
            border-color: var(--accent);
            background: var(--accent-soft);
          }

          .task-title {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            color: var(--ink);
            font-weight: 750;
          }

          .task-title span:first-child {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .task-meta {
            margin-top: 5px;
            color: var(--muted);
            font-size: 13px;
          }

          .task-detail {
            padding: 16px;
          }

          .empty {
            padding: 30px 16px;
            color: var(--muted);
            text-align: center;
          }

          .info-list {
            display: grid;
            gap: 8px;
            margin: 0 0 14px;
          }

          .info-row {
            display: grid;
            grid-template-columns: 120px minmax(0, 1fr);
            gap: 12px;
            padding: 9px 0;
            border-bottom: 1px solid var(--line);
          }

          .info-row strong {
            color: var(--muted);
            font-size: 13px;
          }

          .info-row span {
            overflow-wrap: anywhere;
          }

          pre {
            min-height: 220px;
            max-height: 520px;
            margin: 0;
            overflow: auto;
            border-radius: 8px;
            padding: 14px;
            background: var(--code);
            color: #e5e7eb;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 13px;
            line-height: 1.5;
            white-space: pre-wrap;
          }

          .error {
            margin: 12px 16px 0;
            color: var(--danger);
            font-weight: 650;
          }

          @media (max-width: 900px) {
            .hero {
              align-items: stretch;
              flex-direction: column;
            }

            .actions,
            .focus-actions {
              flex-wrap: wrap;
            }

            main {
              grid-template-columns: 1fr;
            }

            .info-row {
              grid-template-columns: 1fr;
              gap: 3px;
            }
          }
        </style>
      </head>
      <body>
        <header>
          <div class="wrap hero">
            <div>
              <h1>Local Agent Relay</h1>
              <p>只把当前最需要关注的 Agent 任务放在前面，细节按需展开。</p>
            </div>
            <div class="actions">
              <a class="button" href="/docs">API Docs</a>
              <a class="button" href="/health">Health</a>
              <button id="refreshButton" type="button">刷新</button>
            </div>
          </div>
        </header>

        <main class="wrap">
          <section class="focus" id="focusPanel">
            <div class="focus-head">
              <h2>现在关注</h2>
              <span id="focusStatus" class="status">加载中</span>
            </div>
            <h3 id="focusTitle" class="focus-title">正在读取任务</h3>
            <p id="focusMessage" class="focus-message">稍等一下，我正在同步控制平面的最新状态。</p>
            <div class="focus-actions">
              <button id="focusRefreshButton" type="button">刷新状态</button>
              <button id="focusInspectButton" type="button">查看详情</button>
            </div>
          </section>

          <section class="panel">
            <div class="panel-head">
              <h2>创建任务</h2>
            </div>
            <form id="taskForm">
              <label>
                标题
                <input id="title" name="title" value="问 Gemma" autocomplete="off" required>
              </label>
              <label>
                想让 Agent 做什么
                <textarea id="instruction" name="instruction" required>告诉我现在几点了</textarea>
              </label>
              <button id="submitButton" class="primary" type="submit">创建并执行</button>
            </form>
            <details>
              <summary>高级设置</summary>
              <div class="details-body">
                <label>
                  Executor
                  <select id="executor" name="executor">
                    <option value="gemma" selected>Gemma 本地助手</option>
                    <option value="shell">shell</option>
                  </select>
                </label>
                <div id="shellSettings" hidden>
                  <label style="margin-top: 12px;">
                    Shell Command
                    <textarea id="command" name="command">echo task:$LOCAL_AGENT_RELAY_TASK_ID && echo instruction:$LOCAL_AGENT_RELAY_INSTRUCTION</textarea>
                  </label>
                </div>
              </div>
            </details>
            <div id="formError" class="error" hidden></div>
          </section>

          <section class="panel">
            <div class="panel-head">
              <h2>最近任务</h2>
              <p id="taskCount">加载中</p>
            </div>
            <div id="taskList" class="task-list"></div>
          </section>

          <section class="panel" style="grid-column: 1 / -1;">
            <div class="panel-head">
              <h2>任务详情</h2>
              <p id="selectedTaskLabel">未选择</p>
            </div>
            <div id="taskDetail" class="task-detail">
              <div class="empty">选择任务后，这里只显示必要信息；执行日志默认折叠。</div>
            </div>
          </section>
        </main>

        <script>
          const state = {
            selectedTaskId: null,
            tasks: [],
            pollTimer: null,
          };

          const taskList = document.querySelector("#taskList");
          const taskDetail = document.querySelector("#taskDetail");
          const taskCount = document.querySelector("#taskCount");
          const selectedTaskLabel = document.querySelector("#selectedTaskLabel");
          const form = document.querySelector("#taskForm");
          const formError = document.querySelector("#formError");
          const submitButton = document.querySelector("#submitButton");
          const refreshButton = document.querySelector("#refreshButton");
          const focusRefreshButton = document.querySelector("#focusRefreshButton");
          const focusInspectButton = document.querySelector("#focusInspectButton");
          const focusStatus = document.querySelector("#focusStatus");
          const focusTitle = document.querySelector("#focusTitle");
          const focusMessage = document.querySelector("#focusMessage");
          const executorSelect = document.querySelector("#executor");
          const shellSettings = document.querySelector("#shellSettings");

          function escapeHtml(value) {
            return String(value ?? "")
              .replaceAll("&", "&amp;")
              .replaceAll("<", "&lt;")
              .replaceAll(">", "&gt;")
              .replaceAll('"', "&quot;")
              .replaceAll("'", "&#039;");
          }

          function statusClass(status) {
            return `status ${status}`;
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

          async function loadTasks() {
            const tasks = await fetchJson("/tasks");
            state.tasks = tasks;
            taskCount.textContent = `${tasks.length} 个`;
            renderFocus(tasks);

            taskList.innerHTML = tasks.length ? tasks.map((task) => `
              <button class="task ${task.id === state.selectedTaskId ? "active" : ""}" data-task-id="${task.id}" type="button">
                <div class="task-title">
                  <span>${escapeHtml(task.title)}</span>
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
              `<div class="info-row"><strong>${validationIcon(v.status)} ${escapeHtml(v.name)}</strong><span>${escapeHtml(v.adapter)} · ${escapeHtml(v.status)} — ${escapeHtml(v.detail || "")}</span></div>`
            ).join("");
            return `<h3 style="font-size:16px;margin:18px 0 8px;">验收结果</h3><div class="info-list">${rows}</div>`;
          }
          function renderReport(report) {
            if (!report) return "";
            return `<h3 style="font-size:16px;margin:18px 0 8px;">执行报告</h3><pre>${escapeHtml(report)}</pre>`;
          }

          async function loadTaskDetail(taskId) {
            const task = await fetchJson(`/tasks/${taskId}`);
            state.selectedTaskId = task.id;
            selectedTaskLabel.textContent = task.title;

            const logs = task.logs.map((log) => {
              return `[${formatTime(log.created_at)}] ${log.stream}\\n${log.message}`;
            }).join("\\n\\n");

            taskDetail.innerHTML = `
              <div class="info-list">
                <div class="info-row"><strong>状态</strong><span>${escapeHtml(statusLabel(task.status))}</span></div>
                <div class="info-row"><strong>结果</strong><span>${escapeHtml(task.summary || task.error || "等待结果")}</span></div>
                <div class="info-row"><strong>指令</strong><span>${escapeHtml(task.instruction)}</span></div>
              </div>
              ${renderValidations(task.validations)}
              ${renderReport(task.report)}
              <details>
                <summary>技术信息</summary>
                <div class="details-body">
                  <div class="info-list">
                    <div class="info-row"><strong>Executor</strong><span>${escapeHtml(task.executor)}</span></div>
                    <div class="info-row"><strong>Exit Code</strong><span>${escapeHtml(task.exit_code ?? "-")}</span></div>
                    <div class="info-row"><strong>Task ID</strong><span>${escapeHtml(task.id)}</span></div>
                    <div class="info-row"><strong>Command</strong><span>${escapeHtml(task.command || "-")}</span></div>
                  </div>
                </div>
              </details>
              <details>
                <summary>执行日志</summary>
                <div class="details-body">
                  <pre>${escapeHtml(logs || "暂无日志")}</pre>
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

          form.addEventListener("submit", async (event) => {
            event.preventDefault();
            formError.hidden = true;
            submitButton.disabled = true;
            try {
              const payload = {
                title: document.querySelector("#title").value,
                instruction: document.querySelector("#instruction").value,
                executor: document.querySelector("#executor").value,
              };
              if (payload.executor === "shell") {
                payload.command = document.querySelector("#command").value;
              }
              const task = await fetchJson("/tasks", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payload),
              });
              state.selectedTaskId = task.id;
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

          refreshButton.addEventListener("click", () => refresh().catch(console.error));
          focusRefreshButton.addEventListener("click", () => refresh().catch(console.error));
          focusInspectButton.addEventListener("click", () => {
            document.querySelector("#taskDetail").scrollIntoView({behavior: "smooth", block: "start"});
          });
          executorSelect.addEventListener("change", () => {
            shellSettings.hidden = executorSelect.value !== "shell";
          });

          async function startPolling() {
            await loadTasks();
            state.pollTimer = window.setInterval(() => {
              loadTasks().catch(console.error);
            }, 2500);
          }

          startPolling().catch((error) => {
            focusTitle.textContent = "状态读取失败";
            focusMessage.textContent = error.message;
            taskList.innerHTML = `<div class="empty">${escapeHtml(error.message)}</div>`;
          });
        </script>
      </body>
    </html>
    """
