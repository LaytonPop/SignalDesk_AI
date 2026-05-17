"use client";

import { useEffect, useState, useTransition } from "react";

type PanelMode = "ask" | "brief" | "crawl";

type HealthState = {
  status: string;
  environment: string;
  vectorstore_dir: string;
};

type Citation = {
  title: string;
  url: string;
  published_at?: string | null;
  snippet: string;
};

type QueryResult = {
  answer: string;
  citations: Citation[];
  retrieved_count: number;
};

type ReportResult = {
  report_markdown: string;
  citations: string[];
  saved_path: string;
};

type CrawlArticle = {
  title: string;
  url: string;
  published_at?: string | null;
};

type CrawlResult = {
  source_name: string;
  crawled_count: number;
  ingested_count: number;
  articles: CrawlArticle[];
};

type MessageCard = {
  id: string;
  role: "user" | "assistant" | "system";
  title: string;
  content: string;
  stamp: string;
  metrics?: Array<{ label: string; value: string }>;
};

type SourceCard = {
  id: string;
  name: string;
  industry: string;
  coverage: string;
  hotLabel: string;
  note: string;
};

const sourceCards: SourceCard[] = [
  {
    id: "semiconductor",
    name: "Shenzhen SIA",
    industry: "Semiconductor",
    coverage: "协会资讯 / 企业动向 / 产业政策",
    hotLabel: "14 fresh signals",
    note: "适合跑第一次真实抓取闭环。",
  },
  {
    id: "new-energy",
    name: "Energy Watchlist",
    industry: "New Energy",
    coverage: "供应链 / 价格 / 项目审批",
    hotLabel: "Mock feed",
    note: "目前仅用于界面压力测试。",
  },
  {
    id: "ai-stack",
    name: "AI Infra Radar",
    industry: "AI Infra",
    coverage: "模型 / 芯片 / 云服务 / 开源生态",
    hotLabel: "Mock feed",
    note: "适合展示多源聚合形态。",
  },
];

const presets = [
  {
    label: "政策追踪",
    prompt: "总结最近半导体行业资讯中，与政策扶持和地方招商有关的重点变化。",
  },
  {
    label: "竞品动态",
    prompt: "提取最近资讯里出现的重点企业动态，并判断对上下游合作会有什么影响。",
  },
  {
    label: "销售战报",
    prompt: "请把最近24小时的资讯整理成销售同学能直接转发给客户的日报。",
  },
];

const mockCitations: Citation[] = [
  {
    title: "深圳半导体产业链协同大会即将召开",
    url: "https://example.com/brief-1",
    published_at: "2026-05-16",
    snippet: "大会聚焦芯片设计、先进封测与本地供应链协作，释放地方资源整合信号。",
  },
  {
    title: "协会发布重点企业投融资观察",
    url: "https://example.com/brief-2",
    published_at: "2026-05-15",
    snippet: "多家设备与材料企业进入新一轮资本窗口，融资节奏与扩产意愿同步提升。",
  },
];

function stampNow() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

async function parseJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  const data = text ? (JSON.parse(text) as T | { detail?: string; error?: string }) : {};

  if (!response.ok) {
    const message =
      typeof data === "object" && data !== null
        ? ("detail" in data && typeof data.detail === "string" && data.detail) ||
          ("error" in data && typeof data.error === "string" && data.error) ||
          `Request failed with status ${response.status}`
        : `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return data as T;
}

export function IntelligenceWorkbench() {
  const [mode, setMode] = useState<PanelMode>("ask");
  const [mockMode, setMockMode] = useState(true);
  const [health, setHealth] = useState<HealthState | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [selectedSource, setSelectedSource] = useState(sourceCards[0].id);
  const [prompt, setPrompt] = useState("今天半导体行业里最值得业务团队跟进的三条变化是什么？");
  const [reportDate, setReportDate] = useState("");
  const [lookbackHours, setLookbackHours] = useState("24");
  const [crawlPath, setCrawlPath] = useState("config/sources/sample_industry_site.json");
  const [maxArticles, setMaxArticles] = useState("6");
  const [lastCitations, setLastCitations] = useState<Citation[]>(mockCitations);
  const [lastReport, setLastReport] = useState(
    [
      "# Morning Brief",
      "",
      "## 今日重点",
      "- 产业协同和地方支持信号增多，适合跟进区域客户。",
      "- 设备与材料企业融资活跃，说明扩产预期在升温。",
      "",
      "## 建议动作",
      "- 更新客户拜访话术。",
      "- 标注潜在合作伙伴与渠道窗口。",
    ].join("\n"),
  );
  const [messages, setMessages] = useState<MessageCard[]>([
    {
      id: "boot",
      role: "system",
      title: "Desk Ready",
      stamp: stampNow(),
      content:
        "界面已经准备好。你可以先用 Mock 模式验证交互，再切到 Live API 去打后端接口。",
      metrics: [
        { label: "Mode", value: "Mock" },
        { label: "Source", value: "Shenzhen SIA" },
      ],
    },
  ]);
  const [timeline, setTimeline] = useState<string[]>([
    "Workbench initialized.",
    "Proxy routes waiting for FastAPI.",
    "Preset source cards loaded.",
  ]);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    void refreshHealth();
  }, []);

  async function refreshHealth() {
    try {
      const response = await fetch("/api/health", { cache: "no-store" });
      const data = await parseJson<HealthState>(response);
      setHealth(data);
      setHealthError(null);
      startTransition(() => {
        setTimeline((current) => [`Backend health check passed at ${stampNow()}.`, ...current].slice(0, 6));
      });
    } catch (error) {
      setHealth(null);
      setHealthError(error instanceof Error ? error.message : "Unable to reach backend.");
      startTransition(() => {
        setTimeline((current) => [`Backend health check failed at ${stampNow()}.`, ...current].slice(0, 6));
      });
    }
  }

  function pushMessage(next: MessageCard) {
    setMessages((current) => [next, ...current].slice(0, 18));
  }

  function applyPreset(text: string) {
    setPrompt(text);
    pushMessage({
      id: crypto.randomUUID(),
      role: "system",
      title: "Preset Loaded",
      stamp: stampNow(),
      content: text,
    });
  }

  async function handleAsk() {
    const question = prompt.trim();
    if (!question) return;

    pushMessage({
      id: crypto.randomUUID(),
      role: "user",
      title: "Analyst Prompt",
      stamp: stampNow(),
      content: question,
    });

    if (mockMode) {
      const answer =
        "基于模拟情报流，今天最值得业务团队跟进的变化有三条：一是区域产业协同活动增多，说明本地生态合作窗口正在打开；二是设备与材料企业融资活跃，反映扩产预期在升温；三是协会渠道正在释放更强的产业组织能力，适合把客户沟通从单点产品升级成方案式对话。";
      setLastCitations(mockCitations);
      pushMessage({
        id: crypto.randomUUID(),
        role: "assistant",
        title: "Mock Insight",
        stamp: stampNow(),
        content: answer,
        metrics: [
          { label: "Retrieved", value: "2 citations" },
          { label: "Mode", value: "Mock" },
        ],
      });
      startTransition(() => {
        setTimeline((current) => [`Mock query completed at ${stampNow()}.`, ...current].slice(0, 6));
      });
      return;
    }

    const response = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, topK: 5 }),
    });
    const data = await parseJson<QueryResult>(response);
    setLastCitations(data.citations);
    pushMessage({
      id: crypto.randomUUID(),
      role: "assistant",
      title: "Live Insight",
      stamp: stampNow(),
      content: data.answer,
      metrics: [
        { label: "Retrieved", value: `${data.retrieved_count} chunks` },
        { label: "Mode", value: "Live API" },
      ],
    });
    startTransition(() => {
      setTimeline((current) => [`Live query completed at ${stampNow()}.`, ...current].slice(0, 6));
    });
  }

  async function handleBrief() {
    if (mockMode) {
      const report = [
        "# Industry Brief",
        "",
        "## 今日重点",
        "- 半导体协会渠道活跃，适合强化区域客户联动。",
        "- 设备与材料企业融资升温，说明扩产预期和产线升级信号在变强。",
        "",
        "## 风险提醒",
        "- 行业乐观情绪上升，但短期订单兑现仍需要交叉验证。",
        "",
        "## 建议动作",
        "- 给销售团队补一页话术卡。",
        "- 给战略团队拉一份区域合作对象名单。",
      ].join("\n");
      setLastReport(report);
      pushMessage({
        id: crypto.randomUUID(),
        role: "assistant",
        title: "Mock Daily Brief",
        stamp: stampNow(),
        content: report,
        metrics: [
          { label: "Lookback", value: `${lookbackHours}h` },
          { label: "Mode", value: "Mock" },
        ],
      });
      startTransition(() => {
        setTimeline((current) => [`Mock brief generated at ${stampNow()}.`, ...current].slice(0, 6));
      });
      return;
    }

    const response = await fetch("/api/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        reportDate: reportDate || undefined,
        lookbackHours: Number(lookbackHours),
        topK: 8,
      }),
    });
    const data = await parseJson<ReportResult>(response);
    setLastReport(data.report_markdown);
    pushMessage({
      id: crypto.randomUUID(),
      role: "assistant",
      title: "Live Daily Brief",
      stamp: stampNow(),
      content: data.report_markdown,
      metrics: [
        { label: "Saved", value: data.saved_path.split("\\").pop() ?? "report.md" },
        { label: "Mode", value: "Live API" },
      ],
    });
    startTransition(() => {
      setTimeline((current) => [`Live brief generated at ${stampNow()}.`, ...current].slice(0, 6));
    });
  }

  async function handleCrawl() {
    if (mockMode) {
      pushMessage({
        id: crypto.randomUUID(),
        role: "system",
        title: "Mock Crawl Snapshot",
        stamp: stampNow(),
        content:
          "模拟抓取完成：抓取 6 篇文章，结构化表格 2 个，向量入库 14 个 chunk。你可以切换到 Live API 后用真实配置重复这个动作。",
        metrics: [
          { label: "Articles", value: maxArticles },
          { label: "Mode", value: "Mock" },
        ],
      });
      startTransition(() => {
        setTimeline((current) => [`Mock crawl finished at ${stampNow()}.`, ...current].slice(0, 6));
      });
      return;
    }

    const response = await fetch("/api/crawl", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sourcePath: crawlPath,
        maxArticles: Number(maxArticles),
        persistRaw: true,
        autoIngest: true,
      }),
    });
    const data = await parseJson<CrawlResult>(response);
    pushMessage({
      id: crypto.randomUUID(),
      role: "system",
      title: "Live Crawl Complete",
      stamp: stampNow(),
      content: `Source ${data.source_name} crawled successfully.`,
      metrics: [
        { label: "Articles", value: `${data.crawled_count}` },
        { label: "Ingested", value: `${data.ingested_count}` },
      ],
    });
    setLastCitations(
      data.articles.slice(0, 4).map((article) => ({
        title: article.title,
        url: article.url,
        published_at: article.published_at,
        snippet: "Crawled article ready for indexing.",
      })),
    );
    startTransition(() => {
      setTimeline((current) => [`Live crawl finished at ${stampNow()}.`, ...current].slice(0, 6));
    });
  }

  async function handlePrimaryAction() {
    try {
      if (mode === "ask") {
        await handleAsk();
        return;
      }

      if (mode === "brief") {
        await handleBrief();
        return;
      }

      await handleCrawl();
    } catch (error) {
      pushMessage({
        id: crypto.randomUUID(),
        role: "system",
        title: "Request Error",
        stamp: stampNow(),
        content: error instanceof Error ? error.message : "Unexpected request failure.",
      });
      startTransition(() => {
        setTimeline((current) => [`Request failed at ${stampNow()}.`, ...current].slice(0, 6));
      });
    }
  }

  const activeSource = sourceCards.find((item) => item.id === selectedSource) ?? sourceCards[0];

  return (
    <main className="shell">
      <div className="shell-inner">
        <section className="masthead">
          <div className="panel hero">
            <div className="eyebrow">
              <span className="eyebrow-dot" />
              SignalDesk AI / Interactive Test Bench
            </div>
            <div>
              <h1>Turn raw industry noise into a working desk.</h1>
            </div>
            <div className="hero-copy">
              <div>
                This first Next.js screen is designed as a front-end pressure test: query RAG, trigger
                crawl jobs, preview daily briefs, and inspect retrieved evidence without waiting for a
                polished product shell.
              </div>
            </div>
            <div className="hero-stats">
              <div className="stat-chip">
                <strong>3 modes</strong>
                <span>Ask, Brief, Crawl</span>
              </div>
              <div className="stat-chip">
                <strong>Proxy-safe</strong>
                <span>Next routes forward to FastAPI</span>
              </div>
              <div className="stat-chip">
                <strong>{mockMode ? "Mock flow on" : "Live API on"}</strong>
                <span>Switch instantly during UI testing</span>
              </div>
            </div>
          </div>

          <aside className="panel status-panel">
            <div className="status-header">
              <div>
                <strong>Backend pulse</strong>
                <div className="muted tiny">FastAPI handshake and local vectorstore state</div>
              </div>
              <button className="secondary-button" onClick={() => void refreshHealth()}>
                Refresh
              </button>
            </div>
            <div className={`status-badge ${health ? "connected" : "disconnected"}`}>
              {health ? "Connected" : "Disconnected"}
            </div>
            <div className="kpi-grid">
              <div className="kpi">
                <strong>{health?.environment ?? "unknown"}</strong>
                <span>Environment</span>
              </div>
              <div className="kpi">
                <strong>{mockMode ? "Mock" : "Live"}</strong>
                <span>Execution lane</span>
              </div>
            </div>
            <div className="mini-card">
              <strong>Vectorstore</strong>
              <span>{health?.vectorstore_dir ?? healthError ?? "No backend response yet."}</span>
            </div>
            <div className="toggle">
              <div>
                <strong>Mock mode</strong>
                <div className="muted tiny">Keep UI fully interactive even before live data works.</div>
              </div>
              <button
                className={`switch ${mockMode ? "on" : ""}`}
                aria-label="Toggle mock mode"
                onClick={() => setMockMode((current) => !current)}
              />
            </div>
          </aside>
        </section>

        <section className="workspace">
          <aside className="sidebar">
            <div className="card">
              <div className="section-header">
                <div>
                  <strong>Source board</strong>
                  <div className="muted tiny">Choose the feed you want this desk to think around.</div>
                </div>
              </div>
              <div className="source-list">
                {sourceCards.map((source) => (
                  <button
                    key={source.id}
                    className={`source-item ${source.id === selectedSource ? "active" : ""}`}
                    onClick={() => setSelectedSource(source.id)}
                  >
                    <div className="source-title-row">
                      <strong>{source.name}</strong>
                      <span className="source-pill">{source.hotLabel}</span>
                    </div>
                    <div className="muted tiny">{source.industry}</div>
                    <div className="tiny">{source.coverage}</div>
                    <div className="muted tiny">{source.note}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="card">
              <div className="section-header">
                <div>
                  <strong>Mission presets</strong>
                  <div className="muted tiny">Drop in a work-style prompt instead of typing from zero.</div>
                </div>
              </div>
              <div className="preset-list">
                {presets.map((preset) => (
                  <button
                    key={preset.label}
                    className="preset-button"
                    onClick={() => applyPreset(preset.prompt)}
                  >
                    <strong>{preset.label}</strong>
                    <div className="muted tiny">{preset.prompt}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="card">
              <div className="section-header">
                <div>
                  <strong>Activity tape</strong>
                  <div className="muted tiny">Fast operational trace while you test the UI.</div>
                </div>
              </div>
              <div className="timeline">
                {timeline.map((item) => (
                  <div key={item} className="timeline-item">
                    <div className="timeline-badge">Log</div>
                    <div className="tiny">{item}</div>
                  </div>
                ))}
              </div>
            </div>
          </aside>

          <section className="console">
            <div className="card">
              <div className="thread-header">
                <div>
                  <strong>Operations console</strong>
                  <div className="muted tiny">
                    Active source: {activeSource.name} / {activeSource.industry}
                  </div>
                </div>
                <div className="pill">{isPending ? "Updating timeline..." : "Ready"}</div>
              </div>

              <div className="mode-switch">
                <button
                  className={`mode-button ${mode === "ask" ? "active" : ""}`}
                  onClick={() => setMode("ask")}
                >
                  Ask
                </button>
                <button
                  className={`mode-button ${mode === "brief" ? "active" : ""}`}
                  onClick={() => setMode("brief")}
                >
                  Brief
                </button>
                <button
                  className={`mode-button ${mode === "crawl" ? "active" : ""}`}
                  onClick={() => setMode("crawl")}
                >
                  Crawl
                </button>
              </div>
            </div>

            <div className="card">
              <div className="thread-header">
                <div>
                  <strong>Thread</strong>
                  <div className="muted tiny">A running record of prompts, results, and system events.</div>
                </div>
              </div>
              <div className="thread">
                {messages.map((message) => (
                  <article key={message.id} className={`thread-card ${message.role}`}>
                    <div className="thread-meta">
                      <span className="thread-title">{message.title}</span>
                      <span>{message.stamp}</span>
                    </div>
                    <div className="thread-copy">{message.content}</div>
                    {message.metrics ? (
                      <div className="thread-metrics">
                        {message.metrics.map((metric) => (
                          <div key={`${message.id}-${metric.label}`} className="metric-chip">
                            {metric.label}: {metric.value}
                          </div>
                        ))}
                      </div>
                    ) : null}
                  </article>
                ))}
              </div>
            </div>

            <div className="card composer">
              <div className="composer-header">
                <div>
                  <strong>Command deck</strong>
                  <div className="muted tiny">
                    {mode === "ask"
                      ? "Interrogate the knowledge base."
                      : mode === "brief"
                        ? "Generate an operator-ready digest."
                        : "Trigger a crawl-and-ingest cycle."}
                  </div>
                </div>
              </div>

              {mode === "ask" ? (
                <div className="composer-grid">
                  <textarea
                    className="textarea"
                    value={prompt}
                    onChange={(event) => setPrompt(event.target.value)}
                    placeholder="Ask for an intelligence summary, risk view, customer angle, or action plan."
                  />
                </div>
              ) : null}

              {mode === "brief" ? (
                <div className="composer-grid">
                  <div className="split-fields">
                    <input
                      className="field"
                      value={reportDate}
                      onChange={(event) => setReportDate(event.target.value)}
                      placeholder="Optional report date, e.g. 2026-05-17"
                    />
                    <input
                      className="field"
                      value={lookbackHours}
                      onChange={(event) => setLookbackHours(event.target.value)}
                      placeholder="24"
                    />
                  </div>
                </div>
              ) : null}

              {mode === "crawl" ? (
                <div className="composer-grid">
                  <input
                    className="field"
                    value={crawlPath}
                    onChange={(event) => setCrawlPath(event.target.value)}
                    placeholder="config/sources/sample_industry_site.json"
                  />
                  <div className="split-fields">
                    <input
                      className="field"
                      value={maxArticles}
                      onChange={(event) => setMaxArticles(event.target.value)}
                      placeholder="6"
                    />
                    <div className="ghost-field">
                      <strong>Raw HTML</strong>
                      <div className="muted tiny">persisted</div>
                    </div>
                  </div>
                </div>
              ) : null}

              <div className="button-row">
                <button className="primary-button" disabled={isPending} onClick={() => void handlePrimaryAction()}>
                  {mode === "ask" ? "Run Analysis" : mode === "brief" ? "Generate Brief" : "Start Crawl"}
                </button>
                <button
                  className="secondary-button"
                  onClick={() => {
                    setMessages((current) => current.slice(-1));
                    setLastCitations(mockCitations);
                    setLastReport("");
                  }}
                >
                  Clear View
                </button>
              </div>
            </div>
          </section>

          <aside className="inspector">
            <div className="card">
              <div className="inspector-header">
                <div>
                  <strong>Evidence dock</strong>
                  <div className="muted tiny">Retrieved context and source links for the last operation.</div>
                </div>
              </div>
              <div className="evidence-list">
                {lastCitations.length ? (
                  lastCitations.map((citation) => (
                    <article key={`${citation.url}-${citation.title}`} className="evidence-card">
                      <strong>{citation.title}</strong>
                      <div className="muted tiny">{citation.published_at ?? "No publish date"}</div>
                      <div className="tiny">{citation.snippet}</div>
                      <a href={citation.url} target="_blank" rel="noreferrer">
                        Open source
                      </a>
                    </article>
                  ))
                ) : (
                  <div className="empty-state">Run a query or crawl to populate evidence cards.</div>
                )}
              </div>
            </div>

            <div className="card">
              <div className="inspector-header">
                <div>
                  <strong>Brief preview</strong>
                  <div className="muted tiny">Rendered as raw markdown so you can judge structure quickly.</div>
                </div>
              </div>
              {lastReport ? (
                <div className="brief-card">
                  <div className="brief-markdown">{lastReport}</div>
                </div>
              ) : (
                <div className="empty-state">Generate a brief to inspect output shape here.</div>
              )}
            </div>

            <div className="card">
              <div className="inspector-header">
                <div>
                  <strong>Desk notes</strong>
                  <div className="muted tiny">What this first screen is meant to validate.</div>
                </div>
              </div>
              <div className="brief-list">
                <div className="brief-card">
                  <strong>Interaction</strong>
                  <div className="tiny">Switch between mock and live without breaking the interface.</div>
                </div>
                <div className="brief-card">
                  <strong>Integration</strong>
                  <div className="tiny">All browser calls stay same-origin through Next.js proxy routes.</div>
                </div>
                <div className="brief-card">
                  <strong>Product direction</strong>
                  <div className="tiny">
                    This layout is already shaped like a future analyst workspace instead of a plain chat box.
                  </div>
                </div>
              </div>
            </div>
          </aside>
        </section>

        <div className="footer-note tiny">
          Frontend default proxy target: <code>INTEL_API_BASE_URL=http://127.0.0.1:8000</code>
        </div>
      </div>
    </main>
  );
}
