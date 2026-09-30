"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { ArrowUpRight, Building2, Car, MapPin, Phone, Search, User, Wallet } from "lucide-react";
import { searchEntities } from "@/lib/api";
import type { EntitySearchResult } from "@/lib/types";

const quickSearches = ["Rohan", "P001", "PH005", "Riverside"];

function EntityIcon({ type }: { type: string }) {
  const Icon = type === "Person" ? User : type === "Organization" ? Building2 : type === "Vehicle" ? Car : type === "Phone" ? Phone : type === "Location" ? MapPin : type === "Account" ? Wallet : Search;
  return <Icon size={19} strokeWidth={1.8} />;
}

export default function EntitiesPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<EntitySearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch(event?: FormEvent<HTMLFormElement>, nextQuery = query) {
    event?.preventDefault();
    const normalized = nextQuery.trim();
    if (!normalized) return;
    setQuery(normalized);
    setLoading(true);
    setSearched(true);
    setError("");
    try {
      setResults(await searchEntities(normalized));
    } catch (cause) {
      setResults([]);
      setError(cause instanceof Error ? cause.message : "Unable to search entities.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-360 p-5 sm:p-7 lg:p-10">
      <header className="max-w-3xl"><p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#b4532a]">Entity intelligence</p><h1 className="mt-3 text-3xl font-bold tracking-tight text-[#183243] sm:text-4xl">Find the canonical record.</h1><p className="mt-3 text-sm leading-6 text-slate-600">Search across people, phones, vehicles, locations, organizations, and accounts. Every result points back to the observed graph.</p></header>

      <section className="mt-8 max-w-4xl rounded-2xl border border-slate-200 bg-white p-4 shadow-lg shadow-slate-900/5 sm:p-6">
        <form onSubmit={handleSearch}>
          <label htmlFor="entity-search" className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">Search authorized records</label>
          <div className="mt-3 flex flex-col gap-3 sm:flex-row"><div className="relative flex-1"><Search size={19} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#b4532a]" /><input id="entity-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Name, identifier, phone, location..." autoComplete="off" className="w-full rounded-xl border border-slate-300 bg-[#f8fafb] py-3.5 pl-12 pr-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#b4532a] focus:bg-white focus:ring-4 focus:ring-[#f5ddd2]" /></div><button type="submit" disabled={loading || !query.trim()} className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#183243] px-6 py-3.5 text-sm font-bold text-white transition hover:bg-[#244759] disabled:cursor-not-allowed disabled:opacity-50">{loading ? "Searching..." : "Search records"}<ArrowUpRight size={16} /></button></div>
        </form>
        <div className="mt-4 flex flex-wrap items-center gap-2"><span className="mr-1 text-[11px] font-semibold text-slate-400">Try a signal</span>{quickSearches.map((item) => <button type="button" key={item} onClick={() => void handleSearch(undefined, item)} className="rounded-full border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:border-[#d99576] hover:bg-[#fff5f0] hover:text-[#9a4525]">{item}</button>)}</div>
      </section>

      <div className="mt-9 flex items-end justify-between gap-3"><div><p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">Search results</p><h2 className="mt-1 text-xl font-bold text-[#183243]">{searched ? `${results.length} matching records` : "Begin with an entity"}</h2></div>{searched && <span className="font-mono text-xs text-slate-400">QUERY / {query}</span>}</div>

      {error && <div role="alert" className="mt-4 max-w-4xl rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>}
      {loading && <div className="mt-4 max-w-4xl rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">Querying the entity catalog...</div>}
      {!loading && !error && !searched && <div className="mt-4 max-w-4xl rounded-xl border border-dashed border-slate-300 bg-white/60 p-10 text-center"><Search size={24} className="mx-auto text-[#b4532a]" /><p className="mt-3 text-sm font-semibold text-[#183243]">Search by canonical name or known identifier</p><p className="mt-1 text-xs text-slate-500">Results are drawn from the connected synthetic graph.</p></div>}
      {!loading && !error && searched && results.length === 0 && <div className="mt-4 max-w-4xl rounded-xl border border-dashed border-slate-300 bg-white/60 p-10 text-center"><p className="text-sm font-semibold text-[#183243]">No matching records</p><p className="mt-1 text-xs text-slate-500">Try a name fragment, canonical ID, or source identifier.</p></div>}
      {!loading && results.length > 0 && <div className="mt-4 grid max-w-5xl gap-3 md:grid-cols-2">{results.map((entity) => <Link key={`${entity.entity_type}-${entity.entity_id}`} href={`/entities/${entity.entity_id}`} className="group flex items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-[#d99576] hover:shadow-md"><span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-[#f6dfd4] text-[#b4532a]"><EntityIcon type={entity.entity_type} /></span><span className="min-w-0 flex-1"><span className="block truncate text-sm font-bold text-[#183243]">{entity.name}</span><span className="mt-1 block text-xs font-semibold text-slate-500">{entity.entity_type} <span className="px-1 text-slate-300">/</span> <span className="font-mono">{entity.entity_id}</span></span>{entity.secondary_identifier && <span className="mt-1 block truncate text-[11px] text-slate-400">{entity.secondary_identifier}</span>}</span><ArrowUpRight size={17} className="text-slate-300 transition group-hover:text-[#b4532a]" /></Link>)}</div>}
    </div>
  );
}