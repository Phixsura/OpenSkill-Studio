"use client";
/** Shared UI atoms for the Experiment Console (ADR-017 Part L). */

import Link from "next/link";
import { usePathname } from "next/navigation";

import { usePlatformAdmin } from "@/lib/use-me";

export function Pill({ value, styles }: { value: string; styles: Record<string, string> }) {
  const cls = styles[value] ?? "bg-slate-100 text-slate-700";
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}>
      {value.replaceAll("_", " ")}
    </span>
  );
}

const TABS = [
  { href: "/dashboard/experiments", label: "Experiments" },
  // platformOnly tabs list/operate platform-admin endpoints — a delegated
  // org operator would only collect 403s there (defect #59)
  { href: "/dashboard/experiments/decisions", label: "Decisions", platformOnly: true },
  { href: "/dashboard/experiments/promotions", label: "Promotions", platformOnly: true },
  { href: "/dashboard/experiments/layers", label: "Layers", platformOnly: true },
  { href: "/dashboard/experiments/holdouts", label: "Holdouts", platformOnly: true },
  { href: "/dashboard/experiments/metrics", label: "Metric Explorer", platformOnly: true },
];

export function ExperimentsNav() {
  const pathname = usePathname();
  const isPlatformAdmin = usePlatformAdmin();
  return (
    <nav className="flex flex-wrap gap-2 border-b pb-2">
      {TABS.filter((tab) => !tab.platformOnly || isPlatformAdmin).map((tab) => {
        const active =
          tab.href === "/dashboard/experiments"
            ? pathname === tab.href || /^\/dashboard\/experiments\/(new|01)/i.test(pathname)
            : pathname.startsWith(tab.href);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`rounded-md px-3 py-1.5 text-sm font-medium ${
              active ? "bg-slate-900 text-white" : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-dashed p-8 text-center text-sm text-slate-500">
      {message}
    </div>
  );
}

export function ErrorBanner({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <div
      role="alert"
      className="rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800"
    >
      {message}
    </div>
  );
}

export function SectionCard({
  title,
  children,
  actions,
}: {
  title: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
}) {
  return (
    <section className="rounded-lg border bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-800">{title}</h2>
        {actions}
      </div>
      {children}
    </section>
  );
}
