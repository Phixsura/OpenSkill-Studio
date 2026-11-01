"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface Incident {
  id: string;
  title: string;
  severity: string;
  status: string;
  system_id: string | null;
  reported_by: string;
  reported_at: string;
}

interface Alert {
  id: string;
  monitor_id: string;
  severity: string;
  status: string;
  title: string;
  created_at: string;
}

const SEVERITY_COLORS: Record<string, string> = {
  info: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  low: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  warning: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  high: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  critical: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

const STATUS_COLORS: Record<string, string> = {
  reported: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  triaging: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  contained: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  investigating: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  remediating: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
  validating: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  closed: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  open: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  acknowledged: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  resolved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
};

function Badge({ label, colors }: { label: string; colors: string }) {
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${colors}`}>
      {label.replace(/_/g, " ")}
    </span>
  );
}

export default function IncidentsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();
  const tab = (searchParams.get("tab") as "incidents" | "alerts") || "incidents";

  const status = searchParams.get("status") || "";
  const page = Number(searchParams.get("page") || "1");

  const incidentParams = new URLSearchParams({ page: String(page), per_page: "20" });
  if (status) incidentParams.set("status", status);

  const { data: incidentData, isLoading: iLoading } = useQuery({
    queryKey: ["trust-incidents", orgId, status, page],
    queryFn: () =>
      apiWithAuth<{ data: Incident[]; meta: { total: number; has_more: boolean } }>(
        `/orgs/${orgId}/trust/incidents?${incidentParams}`,
      ),
    enabled: tab === "incidents",
  });

  const { data: alertData, isLoading: aLoading } = useQuery({
    queryKey: ["trust-alerts", orgId, page],
    queryFn: () =>
      apiWithAuth<{ data: Alert[]; meta: { total: number; has_more: boolean } }>(
        `/orgs/${orgId}/trust/alerts?page=${page}&per_page=20`,
      ),
    enabled: tab === "alerts",
  });

  const incidents = incidentData?.data ?? [];
  const alerts = alertData?.data ?? [];
  const total = tab === "incidents" ? (incidentData?.meta?.total ?? 0) : (alertData?.meta?.total ?? 0);
  const hasMore = tab === "incidents" ? (incidentData?.meta?.has_more ?? false) : (alertData?.meta?.has_more ?? false);
  const isLoading = tab === "incidents" ? iLoading : aLoading;

  const base = `/dashboard/orgs/${orgId}/trust/incidents`;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Incidents & Alerts</h1>

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {(["incidents", "alerts"] as const).map((t) => (
          <button
            key={t}
            onClick={() => {
              const p = new URLSearchParams();
              p.set("tab", t);
              router.push(`${base}?${p}`);
            }}
            className={`px-4 py-2 text-sm font-medium border-b-2 ${
              tab === t
                ? "border-[hsl(var(--primary))] text-[hsl(var(--primary))]"
                : "border-transparent text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
            }`}
          >
            {t === "incidents" ? "Incidents" : "Monitor Alerts"}
          </button>
        ))}
      </div>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}

      {/* Incidents Tab */}
      {tab === "incidents" && !isLoading && (
        <div className="space-y-4">
          <select
            value={status}
            onChange={(e) => {
              const p = new URLSearchParams();
              p.set("tab", "incidents");
              if (e.target.value) p.set("status", e.target.value);
              p.set("page", "1");
              router.push(`${base}?${p}`);
            }}
            className="rounded-md border px-3 py-1.5 text-sm bg-transparent"
          >
            <option value="">All Statuses</option>
            {["reported", "triaging", "contained", "investigating", "remediating", "validating", "closed"].map(
              (s) => <option key={s} value={s}>{s.replace(/_/g, " ")}</option>,
            )}
          </select>

          {incidents.length === 0 ? (
            <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
              No incidents found.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-lg border">
              <table className="w-full text-sm">
                <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                  <tr>
                    <th className="px-4 py-2 font-medium">Title</th>
                    <th className="px-4 py-2 font-medium">Severity</th>
                    <th className="px-4 py-2 font-medium">Status</th>
                    <th className="px-4 py-2 font-medium">Reported</th>
                  </tr>
                </thead>
                <tbody>
                  {incidents.map((i) => (
                    <tr key={i.id} className="border-b last:border-0 hover:bg-[hsl(var(--secondary))]">
                      <td className="px-4 py-2 font-medium">{i.title}</td>
                      <td className="px-4 py-2">
                        <Badge label={i.severity} colors={SEVERITY_COLORS[i.severity] || ""} />
                      </td>
                      <td className="px-4 py-2">
                        <Badge label={i.status} colors={STATUS_COLORS[i.status] || ""} />
                      </td>
                      <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">
                        {new Date(i.reported_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Alerts Tab */}
      {tab === "alerts" && !isLoading && (
        <>
          {alerts.length === 0 ? (
            <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
              No alerts triggered.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-lg border">
              <table className="w-full text-sm">
                <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                  <tr>
                    <th className="px-4 py-2 font-medium">Alert</th>
                    <th className="px-4 py-2 font-medium">Severity</th>
                    <th className="px-4 py-2 font-medium">Status</th>
                    <th className="px-4 py-2 font-medium">Triggered</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.map((a) => (
                    <tr key={a.id} className="border-b last:border-0 hover:bg-[hsl(var(--secondary))]">
                      <td className="px-4 py-2 font-medium">{a.title}</td>
                      <td className="px-4 py-2">
                        <Badge label={a.severity} colors={SEVERITY_COLORS[a.severity] || ""} />
                      </td>
                      <td className="px-4 py-2">
                        <Badge label={a.status} colors={STATUS_COLORS[a.status] || ""} />
                      </td>
                      <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">
                        {new Date(a.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* Pagination */}
      {total > 0 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-[hsl(var(--muted-foreground))]">{total} total</p>
          <div className="flex gap-2">
            <button
              disabled={page <= 1}
              onClick={() => {
                const p = new URLSearchParams(searchParams);
                p.set("page", String(page - 1));
                router.push(`${base}?${p}`);
              }}
              className="rounded-md border px-3 py-1 text-sm disabled:opacity-50"
            >
              Previous
            </button>
            <button
              disabled={!hasMore}
              onClick={() => {
                const p = new URLSearchParams(searchParams);
                p.set("page", String(page + 1));
                router.push(`${base}?${p}`);
              }}
              className="rounded-md border px-3 py-1 text-sm disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
