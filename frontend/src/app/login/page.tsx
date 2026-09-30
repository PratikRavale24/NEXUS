"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { loginMock } from "../../lib/api";
import type { UserRole } from "../../lib/types";

const roles: { value: UserRole; label: string; description: string }[] = [
  { value: "INVESTIGATOR", label: "Investigator", description: "Explore entities, networks, timelines, and cases." },
  { value: "ANALYST", label: "Analyst", description: "Review analytical findings and intelligence patterns." },
  { value: "SUPERVISOR", label: "Supervisor", description: "Oversee cases, audits, and operational status." },
  { value: "ADMIN", label: "Administrator", description: "Manage the full prototype workspace." },
];

export default function LoginPage() {
  const router = useRouter();
  const [role, setRole] = useState<UserRole>("INVESTIGATOR");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await loginMock(role);
      router.replace("/dashboard");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to start the mock session.");
    } finally {
      setLoading(false);
    }
  }

  return <main className="flex min-h-screen items-center justify-center bg-[#edf2f3] px-5 py-12"><div className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-900/10"><div className="mb-8 flex items-center gap-3"><span className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#183243] text-xl font-bold text-[#f0b49a]">N</span><div><p className="text-lg font-bold tracking-[0.18em] text-[#183243]">NEXUS</p><p className="text-xs uppercase tracking-[0.16em] text-slate-500">Network intelligence</p></div></div><div className="mb-7 rounded-xl border border-[#d99576]/40 bg-[#fff6f1] p-4"><p className="text-xs font-bold uppercase tracking-[0.16em] text-[#9a4425]">Development mock environment</p><p className="mt-2 text-sm leading-6 text-slate-700">Choose a prototype role to explore synthetic data. This is not production authentication and must not be used for real operational access.</p></div><form onSubmit={submit} className="space-y-5"><label className="block text-sm font-semibold text-slate-700" htmlFor="role">Prototype role<select id="role" value={role} onChange={(event) => setRole(event.target.value as UserRole)} className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-3 text-sm font-normal outline-none focus:border-[#b4532a] focus:ring-2 focus:ring-[#f0b49a]/50">{roles.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label><p className="text-sm text-slate-500">{roles.find((item) => item.value === role)?.description}</p>{error && <p role="alert" className="text-sm text-red-700">{error}</p>}<button type="submit" disabled={loading} className="w-full rounded-lg bg-[#183243] px-4 py-3 text-sm font-bold text-white transition hover:bg-[#244a5d] disabled:cursor-wait disabled:opacity-60">{loading ? "Starting session..." : "Enter workspace"}</button></form></div></main>;
}