import type { Metadata } from "next";
import "./globals.css";
import AppShell from "../../components/layout/AppShell";

export const metadata: Metadata = {
  title: "NEXUS | Criminal Network Intelligence",
  description: "Explainable criminal network intelligence for authorized investigative analysis.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className="h-full antialiased"
    >
      <body>
        <AppShell>
          {children}
        </AppShell>
      </body>
    </html>
  );
}
