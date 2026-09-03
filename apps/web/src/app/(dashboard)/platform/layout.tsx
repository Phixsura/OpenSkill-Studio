"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { cn } from "@/lib/utils";
import { useMe } from "@/lib/use-me";

// R101[M28]: per-tab role gates — every platform role saw all 9 tabs, then
// hit server-side 403s on the admin/billing-only ones. `roles: null` = any
// platform role; otherwise the user needs one of the listed roles.
// platform_support keeps Tenants (read-only server-side) per #27 §11.2.
const TABS: { slug: string; label: string; roles: string[] | null }[] = [
  { slug: "", label: "Dashboard", roles: null },
  {
    slug: "tenants",
    label: "Tenants",
    roles: ["platform_admin", "billing_admin", "platform_support"],
  },
  { slug: "plans", label: "Plans", roles: ["platform_admin", "billing_admin"] },
  { slug: "pricing", label: "Pricing", roles: ["platform_admin", "billing_admin"] },
  { slug: "usage", label: "Usage", roles: null },
  { slug: "invoices", label: "Invoices", roles: ["platform_admin", "billing_admin"] },
  { slug: "settlements", label: "Settlements", roles: ["platform_admin", "billing_admin"] },
  { slug: "partners", label: "Partners", roles: ["platform_admin", "billing_admin"] },
  { slug: "audit", label: "Audit", roles: null },
];

export default function PlatformLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { data, isLoading, isError, refetch } = useMe();
  const me = data?.data;
  const allowed = me != null && ((me.platform_roles?.length ?? 0) > 0 || me.role === "admin");
  // R101[M28]: role === "admin" grants every tab; otherwise a tab shows only
  // when the user holds one of its required platform roles.
  const platformRoles = me?.platform_roles ?? [];
  const visibleTabs = TABS.filter(
    (tab) =>
      me?.role === "admin" || tab.roles == null || tab.roles.some((r) => platformRoles.includes(r)),
  );

  useEffect(() => {
    if (!isLoading && me != null && !allowed) router.replace("/dashboard");
  }, [isLoading, me, allowed, router]);

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  // R101[M26]: a network error on /auth/me left the pane permanently blank
  // (me == null → !allowed → null) with no way to recover short of a reload.
  if (isError) {
    return (
      <div className="space-y-3">
        <p className="text-sm text-red-600">Could not load your platform access.</p>
        <button
          onClick={() => refetch()}
          className="rounded-md border px-3 py-1.5 text-sm hover:bg-[hsl(var(--secondary))]"
        >
          Retry
        </button>
      </div>
    );
  }
  if (!allowed) return null;

  return (
    <div className="space-y-6">
      <div className="flex gap-1 overflow-x-auto border-b">
        {visibleTabs.map((tab) => {
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
