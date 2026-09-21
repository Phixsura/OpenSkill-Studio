"use client";
/** Shared UI atoms for the Ecosystem workspace. */

import Link from "next/link";
import { usePathname } from "next/navigation";

export function Pill({ value, styles }: { value: string; styles: Record<string, string> }) {
  const cls = styles[value] ?? "bg-slate-100 text-slate-700";
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}>
      {value.replaceAll("_", " ")}
    </span>
  );
}

const TABS = [
  { href: "/dashboard/ecosystem", label: "Overview" },
  { href: "/dashboard/ecosystem/sources", label: "Sources" },
  { href: "/dashboard/ecosystem/discoveries", label: "Discoveries" },
  { href: "/dashboard/ecosystem/catalog", label: "Catalog" },
  { href: "/dashboard/ecosystem/changes", label: "Change Feed" },
  { href: "/dashboard/ecosystem/pricing", label: "Pricing" },
  { href: "/dashboard/ecosystem/benchmarks", label: "Benchmark Lab" },
  { href: "/dashboard/ecosystem/review", label: "Blind Review" },
  { href: "/dashboard/ecosystem/components", label: "Components" },
  { href: "/dashboard/ecosystem/watchlists", label: "Watchlists" },
];

export function EcosystemNav() {
  const pathname = usePathname();
  return (
    <div className="flex flex-wrap gap-2 border-b pb-3">
      {TABS.map((tab) => {
        const active =
          tab.href === "/dashboard/ecosystem"
            ? pathname === tab.href
            : pathname.startsWith(tab.href);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`rounded-md px-3 py-1.5 text-sm ${
              active
                ? "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]"
                : "bg-[hsl(var(--secondary))] hover:opacity-80"
            }`}
          >
            {tab.label}
          </Link>
        );
      })}
    </div>
  );
}

export function EmptyState({ icon, text }: { icon: string; text: string }) {
  return (
    <div className="rounded-lg border bg-[hsl(var(--card))] p-12 text-center shadow-sm">
      <div className="mb-4 text-4xl">{icon}</div>
      <p className="text-[hsl(var(--muted-foreground))]">{text}</p>
    </div>
  );
}

export function StatCard({
  label,
  value,
  alert,
}: {
  label: string;
  value: number | string;
  alert?: boolean;
}) {
  return (
    <div className="rounded-lg border bg-[hsl(var(--card))] p-4 shadow-sm">
      <div className={`text-2xl font-bold ${alert ? "text-red-600" : ""}`}>{value}</div>
      <div className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">{label}</div>
    </div>
  );
}
