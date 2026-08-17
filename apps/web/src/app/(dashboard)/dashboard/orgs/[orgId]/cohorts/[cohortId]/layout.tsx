"use client";

import Link from "next/link";
import { useParams, usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

export default function CohortLayout({ children }: { children: React.ReactNode }) {
  const { orgId, cohortId } = useParams<{ orgId: string; cohortId: string }>();
  const pathname = usePathname();

  const base = `/dashboard/orgs/${orgId}/cohorts/${cohortId}`;

  const links = [
    { href: base, label: "Overview", exact: true },
    { href: `${base}/members`, label: "Members" },
    { href: `${base}/skills`, label: "Skills" },
    { href: `${base}/projects`, label: "Projects" },
    { href: `${base}/progress`, label: "Progress" },
    { href: `${base}/my-dashboard`, label: "My Dashboard" },
  ];

  return (
    <div>
      <nav className="mb-4 flex gap-1 overflow-x-auto border-b pb-2">
        {links.map((link) => {
          const active = link.exact
            ? pathname === link.href
            : pathname.startsWith(link.href);
          return (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "whitespace-nowrap rounded-md px-3 py-1 text-sm transition-colors",
                active
                  ? "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]"
                  : "text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--secondary))]",
              )}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>
      {children}
    </div>
  );
}
