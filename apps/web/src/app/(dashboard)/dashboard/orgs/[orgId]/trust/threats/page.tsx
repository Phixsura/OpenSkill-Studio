"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface ThreatModel {
  id: string;
  name: string;
  category: string;
  severity: string;
  system_id: string | null;
  attack_vectors: string[];
  mitigations: string[];
  created_at: string;
}

interface Suite {
  id: string;
  name: string;
  threat_model_id: string | null;
  test_count: number;
  created_at: string;
}

interface Run {
  id: string;
  suite_id: string;
  status: string;
  total_tests: number;
  passed: number;
  failed: number;
  created_at: string;
}

const SEVERITY_COLORS: Record<string, string> = {
  info: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  low: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  high: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  critical: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  running: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  completed: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  failed: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

function Badge({ label, colors }: { label: string; colors: string }) {
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${colors}`}>
      {label.replace(/_/g, " ")}
    </span>
  );
}

export default function ThreatsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();
  const tab = (searchParams.get("tab") as "threats" | "suites" | "runs") || "threats";

  const { data: threatData, isLoading: tLoading } = useQuery({
    queryKey: ["trust-threats", orgId],
    queryFn: () => apiWithAuth<{ data: ThreatModel[]; meta: { total: number } }>(`/orgs/${orgId}/trust/threats?per_page=50`),
    enabled: tab === "threats",
  });

  const { data: suiteData, isLoading: sLoading } = useQuery({
    queryKey: ["trust-suites", orgId],
    queryFn: () => apiWithAuth<{ data: Suite[]; meta: { total: number } }>(`/orgs/${orgId}/trust/redteam/suites?per_page=50`),
    enabled: tab === "suites",
  });

  const { data: runData, isLoading: rLoading } = useQuery({
    queryKey: ["trust-runs", orgId],
    queryFn: () => apiWithAuth<{ data: Run[]; meta: { total: number } }>(`/orgs/${orgId}/trust/redteam/runs?per_page=50`),
    enabled: tab === "runs",
  });

  const threats = threatData?.data ?? [];
  const suites = suiteData?.data ?? [];
  const runs = runData?.data ?? [];
  const isLoading = tab === "threats" ? tLoading : tab === "suites" ? sLoading : rLoading;
  const base = `/dashboard/orgs/${orgId}/trust/threats`;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Threat Modeling & Red-Team</h1>

      <div className="flex gap-1 border-b">
        {(["threats", "suites", "runs"] as const).map((t) => (
          <button
            key={t}
            onClick={() => router.push(`${base}?tab=${t}`)}
            className={`px-4 py-2 text-sm font-medium border-b-2 ${
              tab === t
                ? "border-[hsl(var(--primary))] text-[hsl(var(--primary))]"
                : "border-transparent text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
            }`}
          >
            {t === "threats" ? "Threat Models" : t === "suites" ? "Test Suites" : "Test Runs"}
          </button>
        ))}
      </div>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}

      {tab === "threats" && !isLoading && (
        threats.length === 0 ? (
          <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">No threat models defined.</div>
        ) : (
          <div className="space-y-3">
            {threats.map((t) => (
              <div key={t.id} className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">{t.name}</h3>
                  <div className="flex gap-2">
                    <Badge label={t.category} colors="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200" />
                    <Badge label={t.severity} colors={SEVERITY_COLORS[t.severity] || ""} />
                  </div>
                </div>
                {t.attack_vectors.length > 0 && (
                  <p className="mt-2 text-xs text-[hsl(var(--muted-foreground))]">
                    Vectors: {t.attack_vectors.join(", ")}
                  </p>
                )}
                {t.mitigations.length > 0 && (
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">
                    Mitigations: {t.mitigations.join(", ")}
                  </p>
                )}
              </div>
            ))}
          </div>
        )
      )}

      {tab === "suites" && !isLoading && (
        suites.length === 0 ? (
          <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">No test suites created.</div>
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Suite</th>
                  <th className="px-4 py-2 font-medium">Tests</th>
                  <th className="px-4 py-2 font-medium">Created</th>
                </tr>
              </thead>
              <tbody>
                {suites.map((s) => (
                  <tr key={s.id} className="border-b last:border-0 hover:bg-[hsl(var(--secondary))]">
                    <td className="px-4 py-2 font-medium">{s.name}</td>
                    <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">{s.test_count}</td>
                    <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">{new Date(s.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}

      {tab === "runs" && !isLoading && (
        runs.length === 0 ? (
          <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">No test runs executed.</div>
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Run</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 font-medium">Passed</th>
                  <th className="px-4 py-2 font-medium">Failed</th>
                  <th className="px-4 py-2 font-medium">Created</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((r) => (
                  <tr key={r.id} className="border-b last:border-0 hover:bg-[hsl(var(--secondary))]">
                    <td className="px-4 py-2 font-mono text-xs">{r.id.slice(0, 12)}…</td>
                    <td className="px-4 py-2"><Badge label={r.status} colors={STATUS_COLORS[r.status] || ""} /></td>
                    <td className="px-4 py-2 text-green-600 dark:text-green-400">{r.passed}</td>
                    <td className="px-4 py-2 text-red-600 dark:text-red-400">{r.failed}</td>
                    <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">{new Date(r.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}
    </div>
  );
}
