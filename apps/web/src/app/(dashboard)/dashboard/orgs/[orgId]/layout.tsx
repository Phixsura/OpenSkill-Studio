"use client";

import Link from "next/link";
import { useParams, usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

export default function OrgLayout({ children }: { children: React.ReactNode }) {
  const { orgId } = useParams<{ orgId: string }>();
  const pathname = usePathname();

  const base = `/dashboard/orgs/${orgId}`;

  const links = [
    { href: base, label: "Overview", exact: true },
    { href: `${base}/skills`, label: "Skills" },
    { href: `${base}/projects`, label: "Projects" },
    { href: `${base}/cohorts`, label: "Cohorts" },
    { href: `${base}/briefs`, label: "Briefs" },
    { href: `${base}/packs`, label: "Packs" },
    { href: `${base}/workflow-packs`, label: "Workflows" },
    { href: `${base}/workflow-runs`, label: "Runs" },
    { href: `${base}/paths`, label: "Paths" },
    { href: `${base}/installations`, label: "Installed" },
    { href: `${base}/workflow-installations`, label: "WF Installed" },
    { href: `${base}/opportunities`, label: "Opportunities" },
    { href: `${base}/progress`, label: "Progress" },
    { href: `${base}/members`, label: "Members" },
    { href: `${base}/evaluation`, label: "AI Evaluation" },
    { href: `${base}/reviews`, label: "Reviews" },
    { href: `${base}/settings`, label: "Settings" },
  ];

  return (
    <div>
      <nav className="mb-6 flex gap-1 overflow-x-auto border-b pb-2">
        {links.map((link) => {
          const active = link.exact
            ? pathname === link.href
            : pathname.startsWith(link.href);
          return (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "whitespace-nowrap rounded-md px-3 py-1.5 text-sm transition-colors",
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
