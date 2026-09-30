"use client";

import { BriefcaseBusiness, Clock3, FileText, LockKeyhole, RefreshCw, ScanSearch, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { getCase, getCases, startCaseProcessing, updateCaseStatus } from "@/lib/api";
import type { CaseDetail, CaseStatus, CaseSummary } from "@/lib/types";

const statusStyles: Record<CaseStatus, string> = { OPEN: "bg-emerald-50 text-emerald-700", UNDER_REVIEW: "bg-amber-50 text-amber-700", CLOSED: "bg-slate-100 text-slate-600" };

export default function CasesPage() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [selected, setSelected] = useState<CaseDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [processing, setProcessing] = useState(false);

  async function loadCases(caseId?: number) {
    setLoading(true);
    setError("");
    try {
      const items = await getCases();
      setCases(items);
      const id = caseId ?? items[0]?.id;
      setSelected(id ? await getCase(id) : null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load case workspace.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const task = window.setTimeout(() => { void loadCases(); }, 0);
    return () => window.clearTimeout(task);
  }, []);

  async function beginProcessing() {
    const document = selected?.documents[0];
    if (!selected || !document) return;
    setProcessing(true);
    try {
      await startCaseProcessing(selected.id, document.id);
      await loadCases(selected.id);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to start processing.");
    } finally {
      setProcessing(false);
    }
  }

  async function changeStatus(status: CaseStatus) {
    if (!selected) return;
    try {
      await updateCaseStatus(selected.id, status);
      await loadCases(selected.id);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to update case status.");
    }
  }

  return <div className="p-5 lg:p-8">
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div><p className="text-xs font-semibold tracking-widest text-slate-500">CASE OPERATIONS</p><h1 className="mt-2 text-3xl font-semibold text-slate-900">FIR workspace</h1><p className="mt-2 max-w-2xl text-sm text-slate-600">Operational case records and source provenance stay distinct from analytical findings.</p></div>
      <button type="button" onClick={() => void loadCases(selected?.id)} className="inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 shadow-sm"><RefreshCw size={15} /> Refresh</button>
    </div>
    {error && <div className="mt-6 flex items-center justify-between gap-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700"><span>{error}</span><button type="button" onClick={() => void loadCases(selected?.id)} aria-label="Retry loading cases"><RefreshCw size={15} /></button></div>}
    {loading && <div className="mt-8 rounded-xl border border-slate-200 bg-white p-10 text-center text-sm text-slate-500">Loading case queue...</div>}
    {!loading && !error && cases.length === 0 && <div className="mt-8 rounded-xl border border-dashed border-slate-300 p-10 text-center text-sm text-slate-500"><BriefcaseBusiness className="mx-auto mb-3" />No cases have been registered in this prototype.</div>}
    {!loading && !error && cases.length > 0 && <div className="mt-8 grid gap-5 xl:grid-cols-[20rem_1fr]">
      <section className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm"><div className="flex items-center justify-between px-2 pb-3"><h2 className="text-sm font-bold text-slate-800">Queue</h2><span className="text-xs text-slate-500">{cases.length} records</span></div>{cases.map((item) => <button key={item.id} type="button" onClick={() => void loadCases(item.id)} className={`mb-2 w-full rounded-lg border p-3 text-left transition ${selected?.id === item.id ? "border-[#b4532a] bg-[#fff7f3]" : "border-slate-100 hover:border-slate-300"}`}><div className="flex items-center justify-between gap-2"><span className="text-xs font-bold tracking-wide text-slate-500">{item.case_number}</span><span className={`rounded-full px-2 py-1 text-[10px] font-bold ${statusStyles[item.status]}`}>{item.status.replace("_", " ")}</span></div><p className="mt-2 text-sm font-semibold text-slate-800">{item.title}</p></button>)}</section>
      {selected && <section className="space-y-5"><div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-xs font-bold tracking-widest text-slate-500">{selected.case_number}</p><h2 className="mt-2 text-2xl font-semibold text-slate-900">{selected.title}</h2><p className="mt-2 text-sm text-slate-600">{selected.description || "No case description recorded."}</p></div><div className="flex items-center gap-2"><span className={`rounded-full px-3 py-1.5 text-xs font-bold ${statusStyles[selected.status]}`}>{selected.status.replace("_", " ")}</span><select aria-label="Update case status" value={selected.status} onChange={(event) => void changeStatus(event.target.value as CaseStatus)} className="rounded-md border border-slate-200 px-2 py-1.5 text-xs"><option value="OPEN">Open</option><option value="UNDER_REVIEW">Under review</option><option value="CLOSED">Closed</option></select></div></div></div>
        <div className="grid gap-5 lg:grid-cols-2"><div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div className="flex items-center gap-2"><FileText size={17} className="text-[#b4532a]" /><h3 className="font-bold text-slate-800">FIR and documents</h3></div>{selected.documents.length === 0 ? <p className="mt-5 text-sm text-slate-500">No document metadata linked to this case.</p> : selected.documents.map((document) => <div key={document.id} className="mt-4 border-t border-slate-100 pt-4"><div className="flex items-start justify-between gap-3"><div><p className="text-sm font-semibold text-slate-800">{document.filename}</p><p className="mt-1 text-xs text-slate-500">{document.document_type} · {document.processing_status}</p></div><button type="button" onClick={() => void beginProcessing()} disabled={processing} className="inline-flex items-center gap-1 rounded-md bg-[#183243] px-2.5 py-1.5 text-xs font-semibold text-white disabled:opacity-50"><ScanSearch size={13} />{processing ? "Starting" : "Process"}</button></div><p className="mt-3 break-all text-[11px] text-slate-500">Provenance: {document.provenance}</p><p className="mt-1 break-all text-[11px] text-slate-400">SHA-256: {document.sha256_hash}</p></div>)}</div>
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div className="flex items-center gap-2"><Clock3 size={17} className="text-[#b4532a]" /><h3 className="font-bold text-slate-800">Timeline and audit</h3><LockKeyhole size={14} className="ml-auto text-slate-400" /></div>{selected.timeline.length === 0 ? <p className="mt-5 text-sm text-slate-500">No audit events recorded yet.</p> : selected.timeline.map((event, index) => <div key={`${event.timestamp}-${index}`} className="mt-4 border-l-2 border-[#f0b49a] pl-3"><p className="text-xs font-bold text-slate-700">{event.action.replaceAll("_", " ")}</p><p className="mt-1 text-xs text-slate-500">{new Date(event.timestamp).toLocaleString()} · {event.resource_type}</p></div>)}</div></div>
        <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-600"><ShieldCheck size={15} className="text-emerald-600" /> Prototype role boundary: investigator read/process; supervisor/admin status and audit oversight.</div>
      </section>}
    </div>}
  </div>;
}