"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, BriefcaseBusiness, FileSearch, LayoutDashboard, Network, Search, ShieldCheck } from "lucide-react";

const navigation = [
  { label: "Dashboard", caption: "Situation overview", href: "/dashboard", icon: LayoutDashboard },
  { label: "Entity search", caption: "Resolve identity", href: "/entities", icon: Search },
  { label: "Network explorer", caption: "Trace relationships", href: "/entities/P001/network", icon: Network },
  { label: "Findings", caption: "Review analytical leads", href: "/findings", icon: FileSearch },
  { label: "Cases", caption: "FIR work queue", href: "/cases", icon: BriefcaseBusiness },
];

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="fixed inset-y-0 left-0 z-20 hidden w-72 flex-col border-r border-[#263f4c] bg-[#183243] text-white lg:flex">
      <div className="border-b border-white/10 px-7 py-7"><Link href="/dashboard" className="flex items-center gap-3"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#f0b49a] text-lg font-bold text-[#183243]">N</span><span><span className="block text-lg font-bold tracking-[0.2em]">NEXUS</span><span className="mt-0.5 block text-[10px] uppercase tracking-[0.16em] text-slate-300">Network intelligence</span></span></Link></div>
      <div className="px-7 pb-3 pt-8 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">Workspace</div>
      <nav className="space-y-1.5 px-4">{navigation.map(({ label, caption, href, icon: Icon }) => { const active = pathname === href || pathname.startsWith(`${href}/`); return <Link key={href} href={href} className={`group flex items-center gap-3 rounded-xl px-3 py-3 transition ${active ? "bg-white text-[#183243] shadow-lg shadow-black/10" : "text-slate-300 hover:bg-white/10 hover:text-white"}`}><span className={`flex h-9 w-9 items-center justify-center rounded-lg ${active ? "bg-[#f6dfd4] text-[#b4532a]" : "bg-white/10 text-slate-300 group-hover:text-white"}`}><Icon size={17} strokeWidth={1.8} /></span><span className="min-w-0"><span className="block text-sm font-semibold">{label}</span><span className={`mt-0.5 block truncate text-[11px] ${active ? "text-slate-500" : "text-slate-400"}`}>{caption}</span></span></Link>; })}</nav>
      <div className="mt-auto border-t border-white/10 px-5 py-5"><div className="rounded-xl border border-[#d99576]/30 bg-[#b4532a]/15 p-3.5"><div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.16em] text-[#f0b49a]"><Activity size={13} /> Synthetic environment</div><p className="mt-2 text-xs leading-5 text-slate-300">All records are deterministic demonstration data.</p></div><div className="mt-4 flex items-center gap-3 px-1"><span className="flex h-9 w-9 items-center justify-center rounded-full bg-[#e8eef1] text-sm font-bold text-[#183243]">I</span><div><p className="text-sm font-semibold">Investigator</p><p className="text-[11px] text-slate-400">Authorized workspace</p></div><ShieldCheck size={16} className="ml-auto text-emerald-300" /></div></div>
    </aside>
  );
}