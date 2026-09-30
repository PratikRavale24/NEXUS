"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { Bell, ChevronDown, Menu, Search } from "lucide-react";
import Sidebar from "./Sidebar";

type Props = { children: ReactNode };

export default function AppShell({ children }: Props) {
  return (
    <div className="min-h-screen w-full overflow-x-hidden bg-transparent">
      <Sidebar />
      <div className="w-full lg:ml-72 lg:w-auto">
        <header className="sticky top-0 z-10 flex h-18 items-center justify-between border-b border-slate-200/80 bg-[#f7f9fa]/90 px-5 backdrop-blur-md lg:px-9">
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="flex items-center gap-2 lg:hidden" aria-label="NEXUS dashboard"><span className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#183243] text-xs font-bold text-white">N</span><span className="text-sm font-bold tracking-[0.18em] text-[#183243]">NEXUS</span></Link>
            <div className="hidden items-center gap-2 rounded-lg border border-slate-200 bg-white/70 px-3 py-2 text-xs text-slate-500 md:flex"><Search size={15} /><span>Investigation workspace</span></div>
          </div>
          <div className="flex items-center gap-3"><span className="hidden text-[11px] font-semibold uppercase tracking-[0.16em] text-[#b4532a] sm:inline">Demo environment</span><button type="button" aria-label="Notifications" className="rounded-lg p-2 text-slate-500 transition hover:bg-white hover:text-slate-900"><Bell size={18} /></button><button type="button" className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-left shadow-sm" aria-label="Investigator profile"><span className="flex h-7 w-7 items-center justify-center rounded-md bg-[#e8eef1] text-xs font-bold text-[#183243]">I</span><span className="hidden text-xs font-semibold text-slate-700 sm:inline">Investigator</span><ChevronDown size={14} className="text-slate-400" /></button></div>
        </header>
        <nav className="flex w-full items-center gap-2 overflow-x-auto border-b border-slate-200/70 bg-white/50 px-5 py-2.5 text-xs font-semibold text-slate-600 lg:hidden"><Menu size={15} className="mr-1 shrink-0 text-slate-400" /><Link href="/dashboard" className="whitespace-nowrap rounded-md px-2 py-1 hover:bg-white">Dashboard</Link><Link href="/entities" className="whitespace-nowrap rounded-md px-2 py-1 hover:bg-white">Entities</Link><Link href="/entities/P001/network" className="whitespace-nowrap rounded-md px-2 py-1 hover:bg-white">Network</Link><Link href="/findings" className="whitespace-nowrap rounded-md px-2 py-1 hover:bg-white">Findings</Link><Link href="/cases" className="whitespace-nowrap rounded-md px-2 py-1 hover:bg-white">Cases</Link></nav>
        <main className="min-w-0 w-full">{children}</main>
      </div>
    </div>
  );
}