"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Clock3 } from "lucide-react";
import { useEffect, useState } from "react";
import { getEntityTimeline } from "@/lib/api";
import type { TimelineResponse } from "@/lib/types";

export default function TimelinePage() {
  const { entityId } = useParams<{ entityId: string }>();
  const [timeline, setTimeline] = useState<TimelineResponse | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { getEntityTimeline(entityId).then(setTimeline).catch((e: unknown) => setError(e instanceof Error ? e.message : "Unable to load timeline.")); }, [entityId]);
  return <div className="p-8"><Link href={`/entities/${entityId}`} className="inline-flex items-center gap-2 text-sm text-slate-600"><ArrowLeft size={16}/>Entity profile</Link><div className="mt-7"><p className="text-xs font-semibold tracking-widest text-slate-500">TEMPORAL INTELLIGENCE</p><h1 className="mt-2 text-3xl font-semibold">Activity timeline</h1><p className="mt-2 text-sm text-slate-600">Chronological, evidence-linked observations. Date-only records remain date precision.</p></div>{error && <p className="mt-6 rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</p>}{!timeline && !error && <p className="mt-6 text-sm text-slate-500">Loading timeline…</p>}<div className="mt-8 max-w-4xl space-y-3">{timeline?.items.map((item, index) => <article key={`${item.evidence_id}-${index}`} className="flex gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div className="mt-1 rounded-lg bg-sky-50 p-2 text-sky-700"><Clock3 size={18}/></div><div className="min-w-0 flex-1"><div className="flex flex-wrap justify-between gap-2"><p className="font-semibold text-slate-900">{item.event_type.replaceAll("_", " ")}</p><p className="text-xs text-slate-500">{item.timestamp ? new Date(item.timestamp).toLocaleString() : "Date not specified"}</p></div><p className="mt-1 text-sm text-slate-600">{item.description}</p><p className="mt-2 text-xs text-slate-500">{[item.source_type, item.related_entity_name, item.evidence_id].filter(Boolean).join(" · ")}</p></div></article>)}</div></div>;
}
