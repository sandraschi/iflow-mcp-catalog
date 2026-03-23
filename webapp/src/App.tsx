import type { CSSProperties } from "react";
import { useEffect, useMemo, useState } from "react";

type Repo = {
  full_name: string | null;
  html_url: string | null;
  description: string | null;
  stars: number;
  category: string;
  mcp_likelihood: number;
  language: string | null;
  fork: boolean;
  pushed_at: string | null;
  parent_full_name: string | null;
  topics: string[];
};

type CatalogPayload = {
  meta: Record<string, unknown>;
  repos: Repo[];
};

type SortKey = "stars" | "name" | "category" | "mcp_likelihood" | "language" | "pushed_at";

export default function App() {
  const [data, setData] = useState<CatalogPayload | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("");
  const [minScore, setMinScore] = useState(0);
  const [sortKey, setSortKey] = useState<SortKey>("stars");
  const [sortDir, setSortDir] = useState<-1 | 1>(-1);

  useEffect(() => {
    fetch("/api/catalog")
      .then((r) => {
        if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
        return r.json();
      })
      .then((j: CatalogPayload) => {
        setData(j);
        setErr(null);
      })
      .catch((e: Error) => setErr(e.message))
      .finally(() => setLoading(false));
  }, []);

  const categories = useMemo(() => {
    if (!data?.repos) return [];
    return [...new Set(data.repos.map((r) => r.category))].sort();
  }, [data]);

  const rows = useMemo(() => {
    if (!data?.repos) return [];
    const qq = q.trim().toLowerCase();
    let list = data.repos.filter((r) => {
      if (cat && r.category !== cat) return false;
      if ((r.mcp_likelihood ?? 0) < minScore) return false;
      if (!qq) return true;
      const blob = `${r.full_name ?? ""} ${r.description ?? ""} ${(r.topics ?? []).join(" ")}`.toLowerCase();
      return blob.includes(qq);
    });

    const cmp = (a: Repo, b: Repo): number => {
      const dir = sortDir;
      if (sortKey === "stars" || sortKey === "mcp_likelihood") {
        const va = Number(a[sortKey]) || 0;
        const vb = Number(b[sortKey]) || 0;
        if (va === vb) return (a.full_name ?? "").localeCompare(b.full_name ?? "");
        return va < vb ? -dir : dir;
      }
      if (sortKey === "name") {
        return (a.full_name ?? "").localeCompare(b.full_name ?? "") * dir;
      }
      const va = (a[sortKey] ?? "").toString();
      const vb = (b[sortKey] ?? "").toString();
      const c = va.localeCompare(vb);
      return c === 0 ? (a.full_name ?? "").localeCompare(b.full_name ?? "") : c * dir;
    };
    list = [...list].sort(cmp);
    return list;
  }, [data, q, cat, minScore, sortKey, sortDir]);

  const toggleSort = (k: SortKey) => {
    if (sortKey === k) setSortDir((d) => (d === -1 ? 1 : -1));
    else {
      setSortKey(k);
      setSortDir(k === "name" || k === "category" || k === "language" || k === "pushed_at" ? 1 : -1);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: "2rem", color: "var(--muted)" }}>
        Loading catalog…
      </div>
    );
  }

  if (err || !data) {
    return (
      <div style={{ padding: "2rem", maxWidth: 640 }}>
        <h1 style={{ fontSize: "1.2rem" }}>iflow-mcp-catalog</h1>
        <p style={{ color: "var(--muted)" }}>
          {err ?? "No data"}. Run{" "}
          <code style={{ color: "var(--accent)" }}>iflow-mcp-catalog refresh</code> or MCP tool{" "}
          <code style={{ color: "var(--accent)" }}>iflow_catalog_refresh</code>.
        </p>
      </div>
    );
  }

  const meta = data.meta as { org?: string; repo_count?: number; fetched_at?: string };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <header
        style={{
          padding: "1.25rem 1.5rem",
          borderBottom: "1px solid var(--border)",
          background: "var(--panel)",
          backdropFilter: "var(--glass)",
          position: "sticky",
          top: 0,
          zIndex: 10,
        }}
      >
        <h1 style={{ margin: 0, fontSize: "1.15rem", fontWeight: 600 }}>iflow-mcp-catalog</h1>
        <div style={{ color: "var(--muted)", fontSize: "0.85rem", marginTop: "0.35rem" }}>
          org={meta.org ?? "?"} · repos={meta.repo_count ?? data.repos.length} · fetched=
          {String(meta.fetched_at ?? "?")}
        </div>
      </header>

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "0.75rem",
          alignItems: "center",
          padding: "1rem 1.5rem",
        }}
      >
        <label style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
          Search{" "}
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="name / description"
            style={inputStyle}
          />
        </label>
        <label style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
          Category{" "}
          <select value={cat} onChange={(e) => setCat(e.target.value)} style={inputStyle}>
            <option value="">all</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <label style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
          MCP score ≥{" "}
          <input
            type="number"
            min={0}
            max={100}
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value) || 0)}
            style={{ ...inputStyle, width: "4.5rem" }}
          />
        </label>
        <span style={{ color: "var(--muted)", fontSize: "0.85rem" }}>Showing {rows.length} rows</span>
      </div>

      <main style={{ padding: "0 1.5rem 2rem", flex: 1 }}>
        <div
          style={{
            borderRadius: 12,
            overflow: "hidden",
            border: "1px solid var(--border)",
            background: "var(--panel)",
            backdropFilter: "var(--glass)",
          }}
        >
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.88rem" }}>
            <thead>
              <tr style={{ color: "var(--muted)" }}>
                <Th label="★ stars" k="stars" active={sortKey} onSort={toggleSort} align="right" />
                <Th label="repo" k="name" active={sortKey} onSort={toggleSort} />
                <Th label="category" k="category" active={sortKey} onSort={toggleSort} />
                <Th label="mcp" k="mcp_likelihood" active={sortKey} onSort={toggleSort} align="right" />
                <Th label="lang" k="language" active={sortKey} onSort={toggleSort} />
                <Th label="pushed" k="pushed_at" active={sortKey} onSort={toggleSort} />
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr
                  key={r.full_name ?? ""}
                  style={{ borderTop: "1px solid var(--border)" }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLTableRowElement).style.background = "hsl(220 14% 16% / 0.5)";
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLTableRowElement).style.background = "transparent";
                  }}
                >
                  <td style={{ ...tdNum }}>{r.stars}</td>
                  <td style={td}>
                    <a href={r.html_url ?? "#"} target="_blank" rel="noopener noreferrer">
                      {r.full_name}
                    </a>
                    {r.parent_full_name ? (
                      <div style={{ fontSize: "0.78rem", color: "var(--muted)" }}>
                        fork of {r.parent_full_name}
                      </div>
                    ) : null}
                  </td>
                  <td style={td}>
                    <span
                      style={{
                        display: "inline-block",
                        padding: "0.12rem 0.45rem",
                        borderRadius: 999,
                        fontSize: "0.75rem",
                        border: "1px solid var(--border)",
                        background: "hsl(220 14% 18%)",
                      }}
                    >
                      {r.category}
                    </span>
                  </td>
                  <td style={tdNum}>{r.mcp_likelihood}</td>
                  <td style={td}>{r.language ?? "—"}</td>
                  <td style={{ ...td, fontVariantNumeric: "tabular-nums" }}>
                    {(r.pushed_at ?? "").slice(0, 10)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}

const inputStyle: CSSProperties = {
  background: "hsl(220 14% 16%)",
  color: "var(--text)",
  border: "1px solid var(--border)",
  borderRadius: 8,
  padding: "0.4rem 0.55rem",
  fontSize: "0.9rem",
  marginLeft: "0.35rem",
};

const td: CSSProperties = { padding: "0.5rem 0.65rem", textAlign: "left" };
const tdNum: CSSProperties = { ...td, textAlign: "right", fontVariantNumeric: "tabular-nums" };

function Th({
  label,
  k,
  active,
  onSort,
  align,
}: {
  label: string;
  k: SortKey;
  active: SortKey;
  onSort: (k: SortKey) => void;
  align?: "right" | "left";
}) {
  return (
    <th
      style={{
        padding: "0.55rem 0.65rem",
        textAlign: align ?? "left",
        cursor: "pointer",
        userSelect: "none",
        color: active === k ? "var(--accent)" : undefined,
      }}
      onClick={() => onSort(k)}
    >
      {label}
    </th>
  );
}
