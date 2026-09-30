import type { Metadata } from "next";
import "./globals.css";
import AuthGate from "../components/auth/AuthGate";

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
        <AuthGate>{children}</AuthGate>
      </body>
    </html>
  );
}
