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
            --danger: #b42318;
            --ok: #166534;
            --warn: #92400e;
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
            padding: 26px 0 22px;
          }

          h1 {
            margin: 0 0 6px;
            font-size: 34px;
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
            grid-template-columns: 390px minmax(0, 1fr);
            gap: 18px;
            padding: 22px 0 44px;
          }

          section {
            min-width: 0;
          }

          .panel {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: #ffffff;
          }

          .panel-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding: 14px 16px;
            border-bottom: 1px solid var(--line);
          }

          h2 {
            margin: 0;
            font-size: 18px;
            letter-spacing: 0;
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
            min-height: 90px;
            resize: vertical;
          }

          .task-list {
            display: grid;
            gap: 10px;
            padding: 12px;
          }

          .task {
            width: 100%;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 12px;
            background: #ffffff;
            text-align: left;
          }

          .task.active {
            border-color: var(--accent);
            background: #f0fdfa;
          }

          .task-title {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            color: var(--ink);
            font-weight: 750;
          }

          .task-meta {
            margin-top: 5px;
            color: var(--muted);
            font-size: 13px;
          }

          .status {
            flex: 0 0 auto;
            border-radius: 999px;
            padding: 2px 8px;
            background: var(--soft);
            color: var(--muted);
            font-size: 12px;
            font-weight: 750;
          }

          .status.completed {
            background: #dcfce7;
            color: var(--ok);
          }

          .status.executing,
          .status.created {
            background: #fef3c7;
            color: var(--warn);
          }

          .status.failed_execution,
          .status.failed_validation,
          .status.timeout {
            background: #fee4e2;
            color: var(--danger);
          }

          .detail {
            padding: 16px;
          }

          .empty {
            padding: 30px 16px;
            color: var(--muted);
            text-align: center;
          }

          .summary-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin-bottom: 16px;
          }

          .metric {
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 10px;
            background: var(--soft);
          }

          .metric strong {
            display: block;
            font-size: 13px;
            color: var(--muted);
          }

          .metric span {
            display: block;
            margin-top: 4px;
            overflow-wrap: anywhere;
            font-weight: 750;
          }

          pre {
            min-height: 280px;
            max-height: 560px;
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

            .actions {
              flex-wrap: wrap;
            }

            main {
              grid-template-columns: 1fr;
            }

            .summary-grid {
              grid-template-columns: 1fr;
            }
          }
        </style>
      </head>
      <body>
        <header>
          <div class="wrap hero">
            <div>
              <h1>Local Agent Relay</h1>
              <p>本地 Agent 控制平面：提交任务、查看状态、读取执行日志。</p>
            </div>
            <div class="actions">
              <a class="button" href="/docs">API Docs</a>
              <a class="button" href="/health">Health</a>
              <button id="refreshButton" type="button">刷新</button>
            </div>
          </div>
        </header>

        <main class="wrap">
          <section class="panel">
            <div class="panel-head">
              <h2>创建任务</h2>
            </div>
            <form id="taskForm">
              <label>
                标题
                <input id="title" name="title" value="hello shell" autocomplete="off" required>
              </label>
              <label>
                指令
                <textarea id="instruction" name="instruction" required>verify the local control plane can execute a command</textarea>
              </label>
              <label>
                Executor
                <select id="executor" name="executor">
                  <option value="shell">shell</option>
                </select>
              </label>
              <label>
                Shell Command
                <textarea id="command" name="command">echo task:$LOCAL_AGENT_RELAY_TASK_ID && echo instruction:$LOCAL_AGENT_RELAY_INSTRUCTION</textarea>
              </label>
              <button id="submitButton" class="primary" type="submit">创建并执行</button>
            </form>
            <div id="formError" class="error" hidden></div>
          </section>

          <section class="panel">
            <div class="panel-head">
              <h2>任务</h2>
              <p id="taskCount">加载中</p>
            </div>
            <div id="taskList" class="task-list"></div>
          </section>

          <section class="panel" style="grid-column: 1 / -1;">
            <div class="panel-head">
              <h2>任务详情</h2>
              <p id="selectedTaskLabel">未选择</p>
            </div>
            <div id="taskDetail" class="detail">
              <div class="empty">选择一个任务查看日志。</div>
            </div>
          </section>
        </main>

        <script>
          const state = {
            selectedTaskId: null,
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

          async function fetchJson(url, options) {
            const response = await fetch(url, options);
            if (!response.ok) {
              const body = await response.text();
              throw new Error(`${response.status} ${response.statusText}: ${body}`);
            }
            return response.json();
          }

          async function loadTasks() {
            const tasks = await fetchJson("/tasks");
            taskCount.textContent = `${tasks.length} 个任务`;
            taskList.innerHTML = tasks.map((task) => `
              <button class="task ${task.id === state.selectedTaskId ? "active" : ""}" data-task-id="${task.id}" type="button">
                <div class="task-title">
                  <span>${escapeHtml(task.title)}</span>
                  <span class="${statusClass(task.status)}">${escapeHtml(task.status)}</span>
                </div>
                <div class="task-meta">${escapeHtml(task.executor)} · ${escapeHtml(task.created_at)}</div>
              </button>
            `).join("");

            if (!state.selectedTaskId && tasks.length > 0) {
              state.selectedTaskId = tasks[0].id;
            }
            if (state.selectedTaskId) {
              await loadTaskDetail(state.selectedTaskId);
            }
          }

          async function loadTaskDetail(taskId) {
            const task = await fetchJson(`/tasks/${taskId}`);
            state.selectedTaskId = task.id;
            selectedTaskLabel.textContent = task.title;

            const logs = task.logs.map((log) => {
              return `[${log.created_at}] ${log.stream}\\n${log.message}`;
            }).join("\\n\\n");

            taskDetail.innerHTML = `
              <div class="summary-grid">
                <div class="metric"><strong>Status</strong><span>${escapeHtml(task.status)}</span></div>
                <div class="metric"><strong>Exit Code</strong><span>${escapeHtml(task.exit_code ?? "-")}</span></div>
                <div class="metric"><strong>Executor</strong><span>${escapeHtml(task.executor)}</span></div>
              </div>
              <pre>${escapeHtml(logs || "暂无日志")}</pre>
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
                command: document.querySelector("#command").value,
              };
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

          refreshButton.addEventListener("click", () => loadTasks().catch(console.error));

          async function startPolling() {
            await loadTasks();
            state.pollTimer = window.setInterval(() => {
              loadTasks().catch(console.error);
            }, 2500);
          }

          startPolling().catch((error) => {
            taskList.innerHTML = `<div class="empty">${escapeHtml(error.message)}</div>`;
          });
        </script>
      </body>
    </html>
    """
