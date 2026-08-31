"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { cn } from "@/lib/utils";
import { useMe } from "@/lib/use-me";

const TABS = [
  { slug: "", label: "Dashboard" },
  { slug: "tenants", label: "Tenants" },
  { slug: "plans", label: "Plans" },
  { slug: "pricing", label: "Pricing" },
  { slug: "usage", label: "Usage" },
  { slug: "invoices", label: "Invoices" },
  { slug: "settlements", label: "Settlements" },
  { slug: "partners", label: "Partners" },
  { slug: "audit", label: "Audit" },
];

export default function PlatformLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { data, isLoading } = useMe();
  const me = data?.data;
  const allowed = me != null && ((me.platform_roles?.length ?? 0) > 0 || me.role === "admin");

  useEffect(() => {
    if (!isLoading && me != null && !allowed) router.replace("/dashboard");
  }, [isLoading, me, allowed, router]);

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (!allowed) return null;

  return (
    <div className="space-y-6">
      <div className="flex gap-1 overflow-x-auto border-b">
        {TABS.map((tab) => {
          const href = tab.slug ? `/platform/${tab.slug}` : "/platform";
          const active = tab.slug ? pathname.startsWith(href) : pathname === "/platform";
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
