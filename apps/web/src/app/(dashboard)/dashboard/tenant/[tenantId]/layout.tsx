"use client";

import Link from "next/link";
import { usePathname, useParams } from "next/navigation";

import { cn } from "@/lib/utils";

const TABS = [
  { slug: "", label: "Overview" },
  { slug: "billing", label: "Billing" },
  { slug: "credits", label: "Credits" },
  { slug: "budgets", label: "Budgets" },
  { slug: "branding", label: "Branding" },
  { slug: "domains", label: "Domains" },
  { slug: "licenses", label: "Licenses" },
  { slug: "members", label: "Members" },
];

export default function TenantAdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const params = useParams<{ tenantId: string }>();
  const base = `/dashboard/tenant/${params.tenantId}`;

  return (
    <div className="space-y-6">
      <div className="flex gap-1 overflow-x-auto border-b">
        {TABS.map((tab) => {
          const href = tab.slug ? `${base}/${tab.slug}` : base;
          const active = tab.slug ? pathname.startsWith(href) : pathname === base;
          return (
            <Link
              key={tab.slug}
              href={href}
              className={cn(
                "whitespace-nowrap border-b-2 px-3 py-2 text-sm",
                active
                  ? "border-[hsl(var(--primary))] font-medium"
                  : "border-transparent text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]",
              )}
            >
              {tab.label}
            </Link>
          );
        })}
      </div>
      {children}
    </div>
  );
}
