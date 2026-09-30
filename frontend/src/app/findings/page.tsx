"use client";

import Link from "next/link";
import { AlertTriangle, ChevronRight, FileSearch, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { getFindings } from "@/lib/api";
import type { FindingSummary } from "@/lib/types";

export default function FindingsPage() {
  const [findings, setFindings] = useState<FindingSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadFindings = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setFindings(await getFindings());
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load findings.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const task = window.setTimeout(() => {
      void loadFindings();
    }, 0);

    return () => window.clearTimeout(task);
  }, [loadFindings]);

  return (
    <div className="p-8">
      <p className="text-xs font-semibold tracking-widest text-slate-500">EXPLAINABLE FINDINGS</p>
      <h1 className="mt-2 text-3xl font-semibold text-slate-900">Investigative leads</h1>
      <p className="mt-2 max-w-2xl text-sm text-slate-600">Analytical indicators require investigator validation; they are not determinations of guilt.</p>

      {error && (
        <div className="mt-6 flex max-w-3xl flex-wrap items-center justify-between gap-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <span>{error}</span>
          <button type="button" onClick={() => void loadFindings()} className="inline-flex items-center gap-2 rounded-md bg-white px-3 py-2 font-medium text-slate-700 shadow-sm">
            <RefreshCw size={15} /> Retry
          </button>
        </div>
      )}

      {loading && <div className="mt-8 rounded-xl border border-slate-200 bg-white p-10 text-center text-sm text-slate-500">Loading analytical findings...</div>}

      {!loading && !error && findings.length === 0 && (
        <div className="mt-8 rounded-xl border border-dashed border-slate-300 p-10 text-center text-sm text-slate-500">
          <FileSearch className="mx-auto mb-3" />
          No analytical findings are available for this dataset.
        </div>
      )}

      {!loading && !error && findings.length > 0 && (
        <div className="mt-8 grid gap-4 xl:grid-cols-2">
          {findings.map((finding) => (
            <Link key={finding.finding_id} href={`/findings/${encodeURIComponent(finding.finding_id)}`} className="group rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-sky-300 hover:shadow">
              <div className="flex items-start justify-between gap-4">
                <div className="flex gap-3">
                  <AlertTriangle className="mt-0.5 shrink-0 text-amber-600" size={20} />
                  <div>
                    <p className="text-xs font-semibold tracking-wide text-slate-500">{finding.finding_type.replaceAll("_", " ")} · {finding.status}</p>
                    <p className="mt-2 text-sm leading-6 text-slate-800">{finding.description}</p>
                  </div>
                </div>
                <ChevronRight className="shrink-0 text-slate-400 group-hover:text-sky-700" size={20} />
              </div>
              <div className="mt-4 border-t border-slate-100 pt-3 text-xs text-slate-500">{finding.subjects.map((subject) => subject.name ?? subject.entity_id).join(" · ") || "No linked subject"}</div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}