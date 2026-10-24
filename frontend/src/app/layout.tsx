import type { Metadata } from "next";
import Link from "next/link";
import { BriefcaseBusiness, MessageSquare } from "lucide-react";
import ThemeToggle from "../components/ThemeToggle";
import "./globals.css";

const themeInitScript = `
  (() => {
    try {
      const stored = window.localStorage.getItem("assistant-theme");
      const theme =
        stored === "dark" ||
        (stored !== "light" &&
          window.matchMedia("(prefers-color-scheme: dark)").matches)
          ? "dark"
          : "light";
      document.documentElement.dataset.theme = theme;
      document.documentElement.style.colorScheme = theme;
    } catch {
      document.documentElement.dataset.theme = "light";
      document.documentElement.style.colorScheme = "light";
    }
  })();
`;

export const metadata: Metadata = {
  title: "AI Job Assistant",
  description:
    "Resume-aware job discovery with transparent simulated applications.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body>
        <div className="app-shell">
          <aside className="sidebar">
            <Link className="brand" href="/">
              <span className="brand-mark">
                <BriefcaseBusiness size={19} />
              </span>
              <span>Job Assistant</span>
            </Link>
            <nav className="nav-links" aria-label="Main navigation">
              <Link href="/">
                <MessageSquare size={17} /> Assistant
              </Link>
              <Link href="/applications">
                <BriefcaseBusiness size={17} /> Applications
              </Link>
            </nav>
            <ThemeToggle />
            <div className="sidebar-note">
              <strong>Private by default</strong>
              <span>
                Your resume is used for this session and is not stored as an
                original file.
              </span>
            </div>
          </aside>
          <main className="main-content">{children}</main>
        </div>
      </body>
    </html>
  );
}
