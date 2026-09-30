"use client";

export default function GlobalError({ reset }: { error: Error; reset: () => void }) {
  return <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6"><section className="max-w-md rounded-2xl border border-slate-200 bg-white p-7 text-center shadow-sm"><p className="text-xs font-semibold tracking-widest text-slate-500">NEXUS</p><h1 className="mt-3 text-xl font-semibold text-slate-900">This view could not be displayed</h1><p className="mt-2 text-sm text-slate-600">The system did not expose internal error details. Retry the view or return to the dashboard.</p><button onClick={reset} className="mt-5 rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-medium text-white">Retry</button></section></div>;
}
