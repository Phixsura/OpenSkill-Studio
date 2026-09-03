"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Input } from "@/components/ui/input";
import { Pager, QueryError } from "@/components/cp-list";
import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth } from "@/lib/api";
import { formatDate } from "@/lib/cp";

interface PlatformTenant {
  id: string;
  name: string;
  slug: string;
  status: string;
  account_type: string;
  currency: string;
  partner_id: string | null;
  created_at: string;
}

const STATUSES = ["", "trial", "active", "past_due", "suspended", "cancelled", "archived"];

export default function PlatformTenantsPage() {
  // R101[M20]: q fired a request per keystroke — debounce 400ms so typing a
  // slug doesn't spray the backend (and burn the platform rate limit).
  const [rawQ, setRawQ] = useState("");
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);

  useEffect(() => {
    const t = setTimeout(() => {
      setQ(rawQ);
      setPage(1);
    }, 400);
    return () => clearTimeout(t);
  }, [rawQ]);

  const { data, isLoading, isError, error } = useQuery({
    // R101[M9]: page in key + sent to the API — the page silently truncated at
    // the backend default page size with no way to see the rest of the fleet.
    queryKey: ["platform-tenants", q, status, page],
    queryFn: () => {
      const params = new URLSearchParams({ page: String(page), per_page: "50" });
      if (q) params.set("q", q);
      if (status) params.set("status", status);
      return apiWithAuth<{ data: PlatformTenant[]; meta: { has_more: boolean } }>(
        `/platform/tenants?${params.toString()}`,
      );
    },
  });
  const tenants = data?.data ?? [];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Input
          className="max-w-xs"
          placeholder="Search name / slug / billing email"
          value={rawQ}
          onChange={(e) => setRawQ(e.target.value)}
        />
        <select
          className="rounded-md border bg-transparent px-3 py-2 text-sm"
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            setPage(1);
          }}
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s || "all statuses"}
            </option>
          ))}
        </select>
      </div>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}
      {/* R101[M17]: query errors rendered as an empty table — an admin couldn't
          tell "no tenants" from "the list endpoint is down". */}
      {isError && <QueryError error={error} what="tenants" />}
      {!isLoading && !isError && (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full text-sm">
            <thead className="border-b bg-[hsl(var(--secondary))] text-left">
              <tr>
                <th className="px-4 py-2 font-medium">Name</th>
                <th className="px-4 py-2 font-medium">Slug</th>
                <th className="px-4 py-2 font-medium">Status</th>
                <th className="px-4 py-2 font-medium">Type</th>
                <th className="px-4 py-2 font-medium">Currency</th>
                <th className="px-4 py-2 font-medium">Created</th>
              </tr>
            </thead>
            <tbody>
              {tenants.map((t) => (
                <tr key={t.id} className="border-b last:border-0">
                  <td className="px-4 py-2">
                    <Link
                      href={`/platform/tenants/${t.id}`}
                      className="font-medium underline-offset-2 hover:underline"
                    >
                      {t.name}
                    </Link>
                  </td>
                  <td className="px-4 py-2 font-mono text-xs">{t.slug}</td>
                  <td className="px-4 py-2">
                    <StatusBadge status={t.status} />
                  </td>
                  <td className="px-4 py-2">{t.account_type}</td>
                  <td className="px-4 py-2">{t.currency}</td>
                  <td className="px-4 py-2">{formatDate(t.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {!isLoading && !isError && (
        <Pager page={page} hasMore={data?.meta?.has_more ?? false} onPage={setPage} />
      )}
    </div>
  );
}
