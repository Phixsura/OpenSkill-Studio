import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Toaster } from "sonner";
import { Providers } from "@/providers";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: {
    default: "OpenSkill Studio",
    template: "%s | OpenSkill Studio",
  },
  description:
    "Project-based training and delivery platform for AI creators.",
  openGraph: {
    title: "OpenSkill Studio",
    description:
      "Project-based training and delivery platform for AI creators.",
    url: process.env.NEXT_PUBLIC_APP_URL,
    siteName: "OpenSkill Studio",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className="min-h-screen bg-[hsl(var(--background))] font-sans text-[hsl(var(--foreground))] antialiased">
        <a href="#main-content" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded-md focus:bg-[hsl(var(--primary))] focus:px-4 focus:py-2 focus:text-[hsl(var(--primary-foreground))]">Skip to content</a>
        <noscript>
          <div style={{ padding: "2rem", textAlign: "center" }}>
            <h1>JavaScript Required</h1>
            <p>OpenSkill Studio requires JavaScript to run. Please enable JavaScript in your browser settings.</p>
          </div>
        </noscript>
        <Providers>
          {children}
          <Toaster richColors position="top-right" />
        </Providers>
      </body>
    </html>
  );
}
