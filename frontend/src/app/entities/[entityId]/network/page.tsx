"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, CircleAlert, Crosshair, Filter, Maximize2, Network, RefreshCw, Search, SlidersHorizontal, UserRound } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { getEntityNetwork } from "@/lib/api";
import type { NetworkEdge, NetworkNode, NetworkResponse } from "@/lib/types";
import NetworkGraph from "./NetworkGraph";

const typeColors: Record<string, string> = { Person: "#0369a1", Phone: "#0f766e", Account: "#7c3aed", Location: "#b45309", Vehicle: "#be123c", Organization: "#475569", Finding: "#b45309", Evidence: "#64748b", Event: "#0f766e" };

export default function NetworkPage() {
  const { entityId: rawEntityId } = useParams<{ entityId: string }>();
  const entityId = decodeURIComponent(rawEntityId);
  const [network, setNetwork] = useState<NetworkResponse | null>(null);
  const [depth, setDepth] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(entityId);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [focusMode, setFocusMode] = useState(false);
  const [fitRequest, setFitRequest] = useState(0);
  const [visibleTypes, setVisibleTypes] = useState<string[]>([]);

  const loadNetwork = useCallback(async (nextDepth = depth) => {
    setLoading(true); setError("");
    try { const response = await getEntityNetwork(entityId, nextDepth); setNetwork(response); setVisibleTypes([...new Set(response.nodes.map((node) => node.entity_type))]); } catch (cause) { setError(cause instanceof Error ? cause.message : "Unable to load network."); } finally { setLoading(false); }
  }, [depth, entityId]);

  useEffect(() => { const timer = window.setTimeout(() => void loadNetwork(1), 0); return () => window.clearTimeout(timer); }, [loadNetwork]);
  const selectedNode = network?.nodes.find((node) => node.id === selectedId) ?? null;
  const selectedEdge = network?.edges.find((edge) => edge.id === selectedEdgeId) ?? null;
  const types = useMemo(() => [...new Set(network?.nodes.map((node) => node.entity_type) ?? [])].sort(), [network]);
  function reset() { setSelectedId(entityId); setSelectedEdgeId(null); setSearch(""); setFocusMode(false); setVisibleTypes(types); }
  function toggleType(type: string) { setVisibleTypes((current) => current.includes(type) ? current.filter((item) => item !== type) : [...current, type]); }

  return <div className="min-h-[calc(100vh-4rem)] p-4 sm:p-6 lg:p-8"><div className="mx-auto max-w-[1700px]">
    <Link href={`/entities/${entityId}`} className="inline-flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900"><ArrowLeft size={16} />Entity profile</Link>
    <header className="mt-5 flex flex-wrap items-end justify-between gap-4"><div><p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#b4532a]">Relationship intelligence</p><h1 className="mt-2 text-2xl font-bold tracking-tight text-[#183243] sm:text-3xl">Network explorer</h1><p className="mt-2 max-w-2xl text-sm text-slate-600">Start with the selected entity. Expand deliberately to inspect second-hop context.</p></div><div className="flex items-center gap-2 text-xs font-semibold text-slate-500"><span className="h-2 w-2 rounded-full bg-emerald-500" />Depth {network?.depth ?? 1} · {network?.nodes.length ?? 0} nodes · {network?.edges.length ?? 0} links</div></header>
    {error && <div role="alert" className="mt-6 flex flex-wrap items-center gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"><CircleAlert size={18} /><span className="flex-1">{error}</span><button type="button" onClick={() => void loadNetwork()} className="inline-flex items-center gap-2 rounded-lg border border-red-300 px-3 py-2 font-semibold hover:bg-red-100"><RefreshCw size={15} />Retry</button></div>}
    {loading && <div className="mt-6 grid min-h-120 place-items-center rounded-2xl border border-slate-200 bg-white text-sm text-slate-500"><span className="inline-flex items-center gap-2"><RefreshCw size={16} className="animate-spin" />Loading bounded network...</span></div>}
    {!loading && network && <div className="mt-6 grid min-h-145 gap-4 lg:grid-cols-[240px_minmax(0,1fr)_300px]">
      <aside className="order-2 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm lg:order-1"><div className="flex items-center justify-between"><h2 className="text-sm font-bold text-[#183243]">Controls</h2><SlidersHorizontal size={16} className="text-slate-400" /></div><label htmlFor="network-search" className="mt-5 block text-xs font-bold uppercase tracking-wider text-slate-500">Search loaded graph</label><div className="relative mt-2"><Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input id="network-search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Name or ID" className="w-full rounded-lg border border-slate-300 py-2 pl-9 pr-3 text-sm outline-none focus:border-[#b4532a]" /></div><button type="button" onClick={() => setFocusMode((value) => !value)} aria-pressed={focusMode} className={`mt-3 inline-flex w-full items-center justify-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold ${focusMode ? "border-[#b4532a] bg-[#fff5f0] text-[#9a4525]" : "border-slate-200 text-slate-600 hover:bg-slate-50"}`}><Crosshair size={15} />{focusMode ? "Focused view" : "Focus selection"}</button><button type="button" onClick={() => setFitRequest((value) => value + 1)} className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50"><Maximize2 size={15} />Fit network</button><button type="button" onClick={reset} className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50"><RefreshCw size={15} />Reset view</button><div className="mt-6 border-t border-slate-100 pt-4"><p className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-500"><Filter size={14} />Entity filters</p><div className="mt-3 space-y-2">{types.map((type) => <label key={type} className="flex cursor-pointer items-center gap-2 text-sm text-slate-700"><input type="checkbox" checked={visibleTypes.includes(type)} onChange={() => toggleType(type)} className="accent-[#b4532a]" /><span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: typeColors[type] ?? "#64748b" }} />{type}</label>)}</div></div><div className="mt-6 border-t border-slate-100 pt-4"><label htmlFor="depth" className="text-xs font-bold uppercase tracking-wider text-slate-500">Explicit expansion</label><select id="depth" value={depth} onChange={(event) => { const next = Number(event.target.value); setDepth(next); void loadNetwork(next); }} className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"><option value={1}>Depth 1 - direct links</option><option value={2}>Depth 2 - expand context</option></select></div></aside>
      <section className="order-1 flex min-h-120 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm lg:order-2"><div className="flex items-center justify-between border-b border-slate-100 px-4 py-3"><div className="flex items-center gap-2 text-sm font-bold text-[#183243]"><Network size={17} className="text-[#b4532a]" />Graph view</div><span className="text-xs text-slate-400">Click a node or relationship for details</span></div><div className="min-h-105 flex-1 bg-[radial-gradient(circle_at_center,#ffffff_0%,#f7fafb_75%)] p-2"><NetworkGraph network={network} visibleTypes={visibleTypes} search={search} focusMode={focusMode} fitRequest={fitRequest} selectedId={selectedId} selectedEdgeId={selectedEdgeId} onNodeSelect={(id) => { setSelectedId(id); setSelectedEdgeId(null); }} onEdgeSelect={(id) => { setSelectedEdgeId(id); setSelectedId(null); }} /></div><div className="flex flex-wrap gap-x-4 gap-y-2 border-t border-slate-100 px-4 py-3 text-[11px] text-slate-500">{types.slice(0, 7).map((type) => <span key={type} className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full" style={{ backgroundColor: typeColors[type] ?? "#64748b" }} />{type}</span>)}<span className="ml-auto">Edge labels appear on selection</span></div></section>
      <aside className="order-3 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"><Inspector node={selectedNode} edge={selectedEdge} rootId={entityId} /></aside>
    </div>}
    {!loading && network && network.nodes.length === 0 && <div className="mt-6 rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center text-sm text-slate-500">No connected entities are available for this record.</div>}
  </div></div>;
}

function Inspector({ node, edge, rootId }: { node: NetworkNode | null; edge: NetworkEdge | null; rootId: string }) {
  if (edge) return <div><p className="text-[10px] font-bold uppercase tracking-widest text-[#b4532a]">Relationship</p><h2 className="mt-2 text-lg font-bold text-[#183243]">{edge.relationship}</h2><dl className="mt-5 space-y-3 text-sm">{[["From", edge.source], ["To", edge.target], ...Object.entries(edge.properties)].map(([label, value]) => <div key={label}><dt className="text-xs uppercase tracking-wide text-slate-400">{label.replaceAll("_", " ")}</dt><dd className="mt-1 break-words text-slate-800">{formatValue(value)}</dd></div>)}</dl></div>;
  if (!node) return <div className="grid min-h-80 place-items-center text-center text-sm text-slate-500"><div><UserRound size={26} className="mx-auto text-slate-300" /><p className="mt-3 font-semibold text-slate-700">Select a node or relationship</p><p className="mt-1 text-xs">The inspector shows only metadata returned by Neo4j.</p></div></div>;
  return <div><div className="flex items-start justify-between gap-3"><div><p className="text-[10px] font-bold uppercase tracking-widest text-[#b4532a]">{node.entity_type}</p><h2 className="mt-2 text-lg font-bold text-[#183243]">{node.label}</h2><p className="mt-1 font-mono text-xs text-slate-500">{node.id}</p></div><span className="rounded-full bg-slate-100 px-2 py-1 text-[10px] font-bold text-slate-500">{node.id === rootId ? "Selected entity" : "Connected"}</span></div><div className="mt-5 border-t border-slate-100 pt-4"><p className="text-xs font-bold uppercase tracking-wider text-slate-400">Observed metadata</p><dl className="mt-3 space-y-3 text-sm">{Object.entries(node.properties).map(([label, value]) => <div key={label}><dt className="text-xs uppercase tracking-wide text-slate-400">{label.replaceAll("_", " ")}</dt><dd className="mt-1 break-words text-slate-800">{formatValue(value)}</dd></div>)}</dl></div><div className="mt-6 flex flex-wrap gap-2">{node.entity_type === "Person" && <><Link href={`/entities/${node.id}`} className="rounded-lg bg-[#183243] px-3 py-2 text-xs font-bold text-white">Profile</Link><Link href={`/entities/${node.id}/timeline`} className="rounded-lg border border-slate-200 px-3 py-2 text-xs font-bold text-slate-700">Timeline</Link><Link href={`/findings?entity=${node.id}`} className="rounded-lg border border-slate-200 px-3 py-2 text-xs font-bold text-slate-700">Findings</Link></>}</div></div>;
}

function formatValue(value: unknown) { if (value === null || value === undefined || value === "") return "Unavailable"; if (typeof value === "object") return JSON.stringify(value); return String(value); }
