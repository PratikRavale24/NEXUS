"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import AppShell from "../../../components/layout/AppShell";
import { getCurrentUser } from "../../lib/api";
import type { AuthUser } from "../../lib/types";

const AuthContext = createContext<{ user: AuthUser | null; refresh: () => Promise<void> }>({ user: null, refresh: async () => {} });

export function useAuth() {
  return useContext(AuthContext);
}

export default function AuthGate({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checking, setChecking] = useState(pathname !== "/login");

  const refresh = useCallback(async () => {
    try {
      const response = await getCurrentUser();
      setUser(response.user);
    } catch (error) {
      setUser(null);
      if ((error as { status?: number }).status === 401) router.replace("/login");
    } finally {
      setChecking(false);
    }
  }, [router]);

  useEffect(() => {
    if (pathname === "/login") {
      return;
    }
    const timer = window.setTimeout(() => void refresh(), 0);
    return () => window.clearTimeout(timer);
  }, [pathname, refresh]);

  if (pathname === "/login") return <AuthContext.Provider value={{ user, refresh }}>{children}</AuthContext.Provider>;
  if (checking || !user) return <div className="flex min-h-screen items-center justify-center bg-[#f7f9fa] text-sm text-slate-500">Checking secure workspace session...</div>;
  return <AuthContext.Provider value={{ user, refresh }}><AppShell>{children}</AppShell></AuthContext.Provider>;
}