import type { Metadata } from "next";
import { Inter } from "next/font/google";
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
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
