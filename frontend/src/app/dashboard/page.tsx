"use client";

import Link from "next/link";
import { Activity, ArrowUpRight, FileSearch, Network, Search, ShieldCheck, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { getFindings, getHealth } from "@/lib/api";
import type { FindingSummary } from "@/lib/types";

const metricCards = [
  { label: "Entities indexed", value: "25", note: "Synthetic dataset", icon: Network, tone: "bg-[#e8eef1] text-[#183243]" },
  { label: "Anomaly candidates", value: "05", note: "Model-generated leads", icon: Sparkles, tone: "bg-[#fff0e9] text-[#b4532a]" },
  { label: "Source records", value: "480+", note: "Across 5 source types", icon: FileSearch, tone: "bg-[#edf3ed] text-[#3f6d51]" },
];

export default function DashboardPage() {
  const [findings, setFindings] = useState<FindingSummary[]>([]);
  const [services, setServices] = useState<Record<string, boolean>>({});

  useEffect(() => {
    getFindings().then(setFindings).catch(() => setFindings([]));
    Promise.allSettled([getHealth(), getHealth("/health/database"), getHealth("/health/neo4j")]).then((results) => setServices({ api: results[0].status === "fulfilled", postgres: results[1].status === "fulfilled", neo4j: results[2].status === "fulfilled", nlp: true }));
  }, []);

  const statusRows = [["API service", services.api], ["PostgreSQL", services.postgres], ["Neo4j graph", services.neo4j], ["NLP pipeline", services.nlp]] as const;

  return (
    <div className="mx-auto max-w-360 p-5 sm:p-7 lg:p-10">
      <header className="relative overflow-hidden rounded-2xl bg-[#183243] px-6 py-8 text-white shadow-xl shadow-[#183243]/10 sm:px-9 sm:py-10">
        <div className="absolute -right-16 -top-24 h-72 w-72 rounded-full border-32 border-white/5" />
        <div className="relative max-w-2xl"><div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.2em] text-[#f0b49a]"><Activity size={13} /> Investigator workspace</div><h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">See the network<br /><span className="text-[#f0b49a]">behind the record.</span></h1><p className="mt-4 max-w-xl text-sm leading-6 text-slate-300">Move from fragmented source records to explainable network signals, evidence-linked findings, and human review.</p><div className="mt-7 flex flex-wrap gap-3"><Link href="/entities" className="inline-flex items-center gap-2 rounded-lg bg-[#f0b49a] px-4 py-2.5 text-sm font-bold text-[#183243] transition hover:bg-[#f7c8b4]"><Search size={16} /> Search entities</Link><Link href="/findings" className="inline-flex items-center gap-2 rounded-lg border border-white/20 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-white/10">Review leads <ArrowUpRight size={16} /></Link></div></div>
      </header>

      <div className="mt-7 flex flex-wrap items-end justify-between gap-3"><div><p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#b4532a]">Situation overview</p><h2 className="mt-1 text-xl font-bold text-[#183243]">Current intelligence picture</h2></div><span className="rounded-full border border-[#e9c6b6] bg-[#fff6f2] px-3 py-1.5 text-[11px] font-semibold text-[#9a4525]">SYNTHETIC DEMONSTRATION DATASET</span></div>

      <div className="mt-4 grid gap-4 md:grid-cols-3">{metricCards.map(({ label, value, note, icon: Icon, tone }) => <section key={label} className="rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm"><div className="flex items-start justify-between"><div><p className="text-sm font-semibold text-slate-600">{label}</p><p className="mt-3 text-3xl font-bold tracking-tight text-[#183243]">{value}</p><p className="mt-1 text-xs text-slate-500">{note}</p></div><span className={`flex h-10 w-10 items-center justify-center rounded-lg ${tone}`}><Icon size={19} /></span></div></section>)}<section className="rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm"><div className="flex items-start justify-between"><div><p className="text-sm font-semibold text-slate-600">Analytical findings</p><p className="mt-3 text-3xl font-bold tracking-tight text-[#183243]">{findings.length.toString().padStart(2, "0")}</p><p className="mt-1 text-xs text-slate-500">Awaiting investigator review</p></div><span className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#f1eee8] text-[#765f34]"><ShieldCheck size={19} /></span></div></section></div>

      <div className="mt-7 grid gap-5 lg:grid-cols-[1.4fr_0.8fr]">
        <section className="rounded-xl border border-slate-200/90 bg-white p-6 shadow-sm"><div className="flex items-start justify-between"><div><p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">Investigation path</p><h2 className="mt-2 text-lg font-bold text-[#183243]">From data to decision</h2></div><Network size={19} className="text-[#b4532a]" /></div><div className="mt-6 grid gap-2 sm:grid-cols-5">{[["01", "Ingest", "Sources"], ["02", "Resolve", "Entities"], ["03", "Connect", "Graph"], ["04", "Explain", "Findings"], ["05", "Review", "Human" ]].map(([number, title, caption], index) => <div key={title} className="relative rounded-lg border border-slate-200 bg-[#f8fafb] p-3.5"><span className="text-[10px] font-bold text-[#b4532a]">{number}</span><p className="mt-3 text-sm font-bold text-[#183243]">{title}</p><p className="mt-1 text-[11px] text-slate-500">{caption}</p>{index < 4 && <span className="absolute -right-2 top-1/2 hidden h-px w-2 bg-[#d3a08a] sm:block" />}</div>)}</div></section>
        <section className="rounded-xl border border-slate-200/90 bg-white p-6 shadow-sm"><div className="flex items-center justify-between"><div><p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">System readiness</p><h2 className="mt-2 text-lg font-bold text-[#183243]">Connected services</h2></div><span className="rounded-full bg-[#edf3ed] px-2.5 py-1 text-[10px] font-bold text-[#3f6d51]">LOCAL</span></div><div className="mt-5 space-y-3">{statusRows.map(([name, online]) => <div key={name} className="flex items-center justify-between border-b border-slate-100 pb-3 last:border-0 last:pb-0"><span className="text-sm text-slate-600">{name}</span><span className={`flex items-center gap-2 text-xs font-bold ${online ? "text-[#3f6d51]" : "text-[#b4532a]"}`}><i className={`h-2 w-2 rounded-full ${online ? "bg-emerald-500" : "bg-orange-400"}`} />{online ? "Available" : "Unavailable"}</span></div>)}</div></section>
      </div>

      <section className="mt-5 rounded-xl border border-[#e9c6b6] bg-[#fff8f5] p-6"><div className="flex flex-wrap items-center justify-between gap-4"><div><p className="text-[10px] font-bold uppercase tracking-[0.18em] text-[#b4532a]">Suggested starting point</p><h2 className="mt-2 text-lg font-bold text-[#183243]">Trace Rohan Patil through the observed network</h2><p className="mt-1 text-sm text-slate-600">Open the canonical entity, inspect connected records, then review the analytical lead with its source references.</p></div><Link href="/entities/P001" className="inline-flex shrink-0 items-center gap-2 rounded-lg bg-[#183243] px-4 py-2.5 text-sm font-bold text-white transition hover:bg-[#244759]">Open P001 <ArrowUpRight size={16} /></Link></div></section>
    </div>
  );
}