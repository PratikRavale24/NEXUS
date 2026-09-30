"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, CheckCircle2, FileText, RefreshCw, ShieldCheck } from "lucide-react";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { getFinding, reviewFinding } from "@/lib/api";
import type { FindingDetail } from "@/lib/types";

const reviewStatuses = ["UNDER_REVIEW", "CONFIRMED", "REJECTED"] as const;
type ReviewStatus = (typeof reviewStatuses)[number];

export default function FindingPage() {
  const { findingId } = useParams<{ findingId: string }>();
  const [finding, setFinding] = useState<FindingDetail | null>(null);
  const [status, setStatus] = useState<ReviewStatus>("UNDER_REVIEW");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState("");

  const loadFinding = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await getFinding(findingId);
      setFinding(result);
      setNotes(result.review_notes ?? "");
      if (reviewStatuses.includes(result.status as ReviewStatus)) {
        setStatus(result.status as ReviewStatus);
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load finding.");
    } finally {
      setLoading(false);
    }
  }, [findingId]);

  useEffect(() => {
    const task = window.setTimeout(() => {
      void loadFinding();
    }, 0);

    return () => window.clearTimeout(task);
  }, [loadFinding]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!finding) return;
    setSaving(true);
    setSaved("");
    setError("");
    try {
      await reviewFinding(finding.finding_id, status, notes);
      setFinding({ ...finding, status, review_notes: notes });
      setSaved("Review state saved to the investigation workflow.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to save review.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="p-8 text-sm text-slate-500">Loading finding record...</div>;

  if (!finding) {
    return (
      <div className="p-8">
        <div className="max-w-xl rounded-xl border border-red-200 bg-red-50 p-6">
          <h1 className="font-semibold text-red-900">Finding unavailable</h1>
          <p className="mt-2 text-sm text-red-800">{error}</p>
          <button type="button" onClick={() => void loadFinding()} className="mt-4 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-medium text-white">
            <RefreshCw size={16} /> Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <Link href="/findings" className="inline-flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900"><ArrowLeft size={16} /> All findings</Link>
      <div className="mt-7 grid gap-6 xl:grid-cols-3">
        <main className="space-y-6 xl:col-span-2">
          <section className="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">
            <p className="text-xs font-semibold tracking-widest text-amber-700">{finding.finding_type.replaceAll("_", " ")} · {finding.status}</p>
            <h1 className="mt-3 text-2xl font-semibold text-slate-900">Candidate finding</h1>
            <p className="mt-3 leading-7 text-slate-700">{finding.description}</p>
            <div className="mt-6 border-t border-slate-100 pt-5">
              <h2 className="font-semibold text-slate-900">Why this was surfaced</h2>
              {finding.reasons.length > 0 ? <ul className="mt-3 space-y-2">{finding.reasons.map((reason) => <li key={reason} className="flex gap-2 text-sm text-slate-700"><CheckCircle2 size={17} className="mt-0.5 shrink-0 text-sky-700" />{reason}</li>)}</ul> : <p className="mt-3 text-sm text-slate-500">No explanation signals were recorded.</p>}
            </div>
          </section>
          <section className="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">
            <div className="flex items-center gap-2"><FileText size={19} className="text-sky-700" /><h2 className="font-semibold text-slate-900">Evidence and provenance</h2></div>
            <p className="mt-2 text-sm text-slate-600">References remain linked to their source records in this synthetic demonstration.</p>
            {finding.evidence.length > 0 ? <div className="mt-4 space-y-2">{finding.evidence.map((evidence) => <div key={evidence.evidence_id} className="flex flex-wrap justify-between gap-2 rounded-lg bg-slate-50 px-4 py-3 text-sm"><span className="font-mono text-slate-800">{evidence.evidence_id}</span><span className="text-slate-500">{[evidence.source_type, evidence.case_id, evidence.timestamp ? new Date(evidence.timestamp).toLocaleString() : null].filter(Boolean).join(" · ")}</span></div>)}</div> : <p className="mt-4 rounded-lg bg-slate-50 p-4 text-sm text-slate-500">No direct evidence references were recorded.</p>}
          </section>
        </main>
        <aside className="h-fit rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-2"><ShieldCheck size={19} className="text-emerald-700" /><h2 className="font-semibold text-slate-900">Investigator review</h2></div>
          <p className="mt-2 text-sm text-slate-600">Review status records an analytical decision about this lead, not a determination of guilt.</p>
          <form onSubmit={submit} className="mt-5 space-y-4">
            <label className="block text-sm font-medium text-slate-700">Review state<select value={status} onChange={(event) => setStatus(event.target.value as ReviewStatus)} className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-200">{reviewStatuses.map((value) => <option key={value} value={value}>{value.replaceAll("_", " ")}</option>)}</select></label>
            <label className="block text-sm font-medium text-slate-700">Review notes<textarea value={notes} onChange={(event) => setNotes(event.target.value)} rows={5} placeholder="Record the investigative rationale..." className="mt-2 w-full resize-y rounded-lg border border-slate-300 px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-200" /></label>
            {error && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
            {saved && <p role="status" className="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800">{saved}</p>}
            <button type="submit" disabled={saving} className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"><ShieldCheck size={16} /> {saving ? "Saving..." : "Save review"}</button>
          </form>
        </aside>
      </div>
    </div>
  );
}