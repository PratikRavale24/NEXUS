"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Clock3, FileSearch, Network } from "lucide-react";
import { useEffect, useState } from "react";
import { getEntity } from "@/lib/api";
import type { EntityProfile } from "@/lib/types";

export default function EntityProfilePage() {
  const params = useParams<{ entityId: string }>();
  const entityId = decodeURIComponent(params.entityId);
  const [entity, setEntity] = useState<EntityProfile | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getEntity(entityId).then(setEntity).catch((cause: unknown) =>
      setError(cause instanceof Error ? cause.message : "Unable to load entity."),
    );
  }, [entityId]);

  if (error) return <div className="p-8 text-sm text-red-700">{error}</div>;
  if (!entity) return <div className="p-8 text-sm text-slate-500">Loading entity record…</div>;
  const person = entity.entity_type === "Person";
  const views = [
    person && ["Network", `/${"entities"}/${entity.entity_id}/network`, Network, "Explore evidence-linked relationships."],
    person && ["Timeline", `/${"entities"}/${entity.entity_id}/timeline`, Clock3, "Review activity in temporal context."],
    ["Findings", `/findings?entity=${entity.entity_id}`, FileSearch, "Review analytical indicators and evidence."],
  ].filter(Boolean) as [string, string, typeof Network, string][];

  return <div className="p-8">
    <Link href="/entities" className="mb-7 inline-flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900"><ArrowLeft size={16} />Entity search</Link>
    <section className="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-6">
        <div><p className="text-xs font-semibold uppercase tracking-widest text-slate-400">{entity.entity_type} record</p><h1 className="mt-2 text-3xl font-semibold text-slate-900">{entity.name}</h1><p className="mt-2 font-mono text-xs text-slate-500">{entity.entity_id}</p></div>
        <div className="grid grid-cols-2 gap-3"><Metric label="Connections" value={entity.connection_count} /><Metric label="Related findings" value={entity.finding_count} /></div>
      </div>
      <div className="mt-8 border-t border-slate-200 pt-6"><h2 className="font-semibold text-slate-900">Investigation views</h2><div className="mt-4 grid gap-3 md:grid-cols-3">{views.map(([label, href, Icon, description]) => <Link key={label} href={href} className="rounded-xl border border-slate-200 p-5 transition hover:border-sky-300 hover:shadow-sm"><Icon size={20} className="text-sky-700"/><p className="mt-3 font-semibold text-slate-900">{label}</p><p className="mt-1 text-xs text-slate-500">{description}</p></Link>)}</div></div>
      <div className="mt-8 border-t border-slate-200 pt-6"><h2 className="font-semibold text-slate-900">Record attributes</h2><div className="mt-4 grid gap-3 md:grid-cols-2">{Object.entries(entity.properties).map(([key, value]) => <div key={key} className="rounded-lg bg-slate-50 p-4"><p className="text-xs uppercase tracking-wide text-slate-500">{key.replaceAll("_", " ")}</p><p className="mt-1 break-all text-sm text-slate-900">{String(value)}</p></div>)}</div></div>
    </section>
  </div>;
}

function Metric({ label, value }: { label: string; value: number }) { return <div className="rounded-xl bg-slate-950 px-5 py-4 text-white"><p className="text-xs text-slate-300">{label}</p><p className="mt-1 text-2xl font-semibold">{value}</p></div>; }
