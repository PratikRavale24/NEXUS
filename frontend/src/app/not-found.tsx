import Link from "next/link";

export default function NotFound() {
  return <div className="p-8"><h1 className="text-2xl font-semibold text-slate-900">View not found</h1><p className="mt-2 text-sm text-slate-600">The requested NEXUS view is not available.</p><Link href="/dashboard" className="mt-5 inline-block rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-medium text-white">Return to dashboard</Link></div>;
}
