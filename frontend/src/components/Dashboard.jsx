import { useEffect, useState } from "react";
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import API from "../api";

const colors = ["#e76f51", "#e9c46a", "#2a9d8f"];

function StatCard({ label, value, detail, accent }) {
  return (
    <article className="stat-card" style={{ "--accent": accent }}>
      <span className="stat-label">{label}</span>
      <strong>{value}</strong>
      <span className="stat-detail">{detail}</span>
    </article>
  );
}

function DistributionChart({ title, data }) {
  return (
    <section className="panel chart-panel">
      <div className="panel-heading">
        <div><span className="eyebrow">Signal map</span><h2>{title}</h2></div>
        <span className="panel-mark">●</span>
      </div>
      <div className="chart-wrap">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" innerRadius="62%" outerRadius="86%" paddingAngle={4} stroke="none">
              {data.map((entry, index) => <Cell key={entry.name} fill={colors[index]} />)}
            </Pie>
            <Tooltip contentStyle={{ border: "1px solid #d6e0df", borderRadius: 8 }} />
          </PieChart>
        </ResponsiveContainer>
        <div className="chart-center"><strong>{data.reduce((total, item) => total + item.value, 0)}</strong><span>tracked</span></div>
      </div>
      <div className="legend">{data.map((entry, index) => <span key={entry.name}><i style={{ background: colors[index] }} />{entry.name} <b>{entry.value}</b></span>)}</div>
    </section>
  );
}

function formatDownloads(value) {
  if (value === null || value === undefined) return "--";
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value;
}

function InvestigationView({ data, onBack }) {
  const { summary, threats, releases } = data;
  const latestThreat = threats.releases?.[0] || {
    threat_score: 0,
    threat_level: "LOW",
    security_flags: [],
  };
  const signals = latestThreat.security_flags || [];

  return (
    <main className="app-shell">
      <header className="topbar"><div className="brand-lockup"><div className="brand-symbol">N</div><div><div className="brand-name">NPMVector</div><div className="brand-subtitle">Investigation workspace</div></div></div><button className="back-button" onClick={onBack}>← Overview</button></header>
      <section className="investigation-hero"><span className="eyebrow">Package investigation</span><h1>{summary.name}</h1><p>Release history and security signals for the monitored package.</p></section>
      <section className="investigation-grid">
        <article className="investigation-metric"><span>Latest version</span><strong>{summary.latest_version || "--"}</strong></article>
        <article className="investigation-metric"><span>Downloads</span><strong>{formatDownloads(summary.downloads)}</strong></article>
        <article className="investigation-metric"><span>Relevance score</span><strong>{summary.relevance_score}</strong></article>
        <article className="investigation-metric"><span>Priority</span><strong>{summary.priority}</strong></article>
      </section>
      <section className="investigation-columns">
        <article className="panel security-card"><div className="panel-heading"><div><span className="eyebrow">Latest release</span><h2>Security analysis</h2></div><span className={`threat-badge ${latestThreat.threat_level.toLowerCase()}`}>{latestThreat.threat_level}</span></div><div className="threat-score"><strong>{latestThreat.threat_score}</strong><span>threat score / 100</span></div><div className="signal-list">{signals.length ? signals.map((flag, index) => <div key={`${flag.type}-${index}`} className="signal signal-warning">! <span>{flag.type.replaceAll("_", " ")}</span></div>) : <><div className="signal">✓ <span>No security signals detected</span></div><div className="signal">✓ <span>No suspicious install script</span></div><div className="signal">✓ <span>Normal release activity</span></div></>}</div></article>
        <article className="panel release-card"><div className="panel-heading"><div><span className="eyebrow">Timeline</span><h2>Release history</h2></div><span className="queue-count">{releases.releases?.length || 0} releases</span></div><div className="release-list">{(releases.releases || []).map((release) => <div className="release-row" key={`${release.version}-${release.detected_at}`}><strong>{release.version}</strong><span>{release.change_type?.replaceAll("_", " ")}</span><small>{release.detected_at ? new Date(release.detected_at).toLocaleDateString() : ""}</small></div>)}</div></article>
      </section>
      <footer><span>NPMVECTOR / INVESTIGATION</span><span>Evidence is explainable, not a malware verdict</span></footer>
    </main>
  );
}

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [packages, setPackages] = useState([]);
  const [highThreats, setHighThreats] = useState([]);
  const [recentReleases, setRecentReleases] = useState([]);
  const [investigation, setInvestigation] = useState(null);
  const [investigationError, setInvestigationError] = useState("");
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    let active = true;
    const loadDashboard = async () => {
      try {
        const [statsResponse, rankingResponse, threatsResponse, releasesResponse] = await Promise.all([
          API.get("/dashboard/stats"),
          API.get("/packages/ranking"),
          API.get("/threats/high"),
          API.get("/dashboard/releases"),
        ]);
        if (!active) return;
        setStats(statsResponse.data);
        setPackages(rankingResponse.data.packages || []);
        setHighThreats(threatsResponse.data.threats || []);
        setRecentReleases(releasesResponse.data.releases || []);
        setLastUpdated(new Date());
        setError("");
      } catch (requestError) {
        if (active) setError("Unable to connect to NPMVector API");
      }
    };
    loadDashboard();
    const refresh = window.setInterval(loadDashboard, 30000);
    return () => { active = false; window.clearInterval(refresh); };
  }, []);

  async function openInvestigation(packageName) {
    try {
      setInvestigationError("");
      const [summary, threats, releases] = await Promise.all([
        API.get(`/packages/${encodeURIComponent(packageName)}/summary`),
        API.get(`/packages/${encodeURIComponent(packageName)}/threats`),
        API.get(`/packages/${encodeURIComponent(packageName)}/releases`),
      ]);
      setInvestigation({ summary: summary.data, threats: threats.data, releases: releases.data });
    } catch (requestError) {
      setInvestigationError(`Unable to load investigation for ${packageName}`);
    }
  }

  if (error && !stats) return <main className="app-shell"><div className="notice">{error}</div></main>;
  if (!stats) return <main className="app-shell"><div className="loading-state">Loading NPMVector...</div></main>;
  if (investigationError) return <main className="app-shell"><div className="notice">{investigationError} <button className="text-button" onClick={() => setInvestigationError("")}>Back</button></div></main>;
  if (investigation) return <InvestigationView data={investigation} onBack={() => setInvestigation(null)} />;

  const priorityData = [
    { name: "High", value: stats.priority.high },
    { name: "Medium", value: stats.priority.medium },
    { name: "Low", value: stats.priority.low },
  ];
  const threatData = [
    { name: "High", value: stats.threats.high },
    { name: "Medium", value: stats.threats.medium },
    { name: "Low", value: stats.threats.low },
  ];

  return (
    <main className="app-shell">
      <div className="ambient ambient-one" /><div className="ambient ambient-two" />
      <header className="topbar"><div className="brand-lockup"><div className="brand-symbol">N</div><div><div className="brand-name">NPMVector</div><div className="brand-subtitle">Supply chain observability</div></div></div><div className="status-pill"><span /> Monitoring active</div></header>
      <section className="hero"><div><span className="eyebrow">Security overview</span><h1>Know what changed<br /><em>before it spreads.</em></h1><p>Release intelligence for the packages your ecosystem depends on.</p></div><div className="hero-meta"><span>Last sync</span><strong>{lastUpdated?.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</strong></div></section>
      {error && <div className="notice">{error}</div>}
      <section className="stats-grid">
        <StatCard label="Packages tracked" value={stats.packages.total} detail={`${stats.packages.monitored} monitored`} accent="#2a9d8f" />
        <StatCard label="High threat releases" value={stats.threats.high} detail={`${stats.releases.total} releases analyzed`} accent="#e76f51" />
        <StatCard label="Requires attention" value={stats.priority.high} detail="high relevance packages" accent="#e9c46a" />
      </section>
      <section className="charts-grid"><DistributionChart title="Relevance distribution" data={priorityData} /><DistributionChart title="Threat distribution" data={threatData} /></section>
      <section className="panel alert-panel"><div className="panel-heading"><div><span className="eyebrow">Immediate review</span><h2>⚠ High threat releases</h2></div><span className="queue-count">{highThreats.length} alerts</span></div>{highThreats.length ? <div className="alert-list">{highThreats.map((item) => <button className="alert-row" key={`${item.package}-${item.version}`} onClick={() => openInvestigation(item.package)}><strong>{item.package}</strong><span>{item.version}</span><b>{item.threat_score}</b></button>)}</div> : <p className="empty-alerts">No high-threat releases require review.</p>}</section>
      <section className="panel attention-panel"><div className="panel-heading table-heading"><div><span className="eyebrow">Change stream</span><h2>Recent releases</h2></div><span className="queue-count">{recentReleases.length} latest</span></div><div className="table-scroll"><table><thead><tr><th>Package</th><th>Previous</th><th>Current</th><th>Threat</th><th>Detected</th></tr></thead><tbody>{recentReleases.map((release) => <tr key={`${release.package}-${release.version}`} className="clickable-row" onClick={() => openInvestigation(release.package)}><td><strong>{release.package}</strong></td><td className="release-version">{release.previous_version || "Initial"}</td><td className="release-version">{release.version}</td><td><span className={`threat-badge ${release.threat_level.toLowerCase()}`}>{release.threat_score} / {release.threat_level}</span></td><td>{release.detected_at ? new Date(release.detected_at).toLocaleDateString() : "--"}</td></tr>)}</tbody></table></div></section>
      <section className="panel attention-panel">
        <div className="panel-heading table-heading"><div><span className="eyebrow">Operational view</span><h2>Package inventory</h2></div><span className="queue-count">{packages.length} packages</span></div>
        <div className="table-scroll"><table><thead><tr><th>Package</th><th>Version</th><th>Downloads</th><th>Relevance</th><th>Priority</th><th>Threat</th></tr></thead><tbody>
          {packages.map((item) => <tr key={item.name} className="clickable-row" onClick={() => openInvestigation(item.name)}><td><strong>{item.name}</strong></td><td className="release-version">{item.version || "--"}</td><td>{formatDownloads(item.downloads)}</td><td>{item.relevance ?? item.score}</td><td><span className={`priority-badge ${item.priority.toLowerCase()}`}>{item.priority}</span></td><td><span className={`threat-badge ${item.threat_level.toLowerCase()}`}>{item.threat_score} / {item.threat_level}</span></td></tr>)}
        </tbody></table></div>
      </section>
      <footer><span>NPMVECTOR / SECURITY OPERATIONS</span><span>Auto-refreshes every 30 seconds</span></footer>
    </main>
  );
}

export default Dashboard;