"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { apiWithAuth } from "@/lib/api";

interface EvidenceItem {
  id: string;
  title: string;
  evidence_type: string;
  status: string;
  version: number;
  source_type: string | null;
  created_at: string;
}

interface AssuranceCase {
  id: string;
  system_id: string;
  title: string;
  claim: string;
  status: string;
  owner_user_id: string;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  valid: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  stale: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  revoked: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  superseded: "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300",
  active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  challenged: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  retired: "bg-gray-300 text-gray-500 dark:bg-gray-700 dark:text-gray-400",
};

const TYPE_LABELS: Record<string, string> = {
  benchmark: "Benchmark",
  experiment: "Experiment",
  evaluation: "Evaluation",
  red_team: "Red Team",
  app_review: "App Review",
  privacy_assessment: "Privacy",
  incident_report: "Incident",
  human_attestation: "Attestation",
  external_audit: "External Audit",
  policy_simulation: "Policy Sim",
  custom: "Custom",
};

function Badge({ label, colors }: { label: string; colors: string }) {
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${colors}`}>
      {label.replace(/_/g, " ")}
    </span>
  );
}

export default function EvidencePage() {
  const { orgId } = useParams<{ orgId: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<"evidence" | "cases">(
    (searchParams.get("tab") as "evidence" | "cases") || "evidence",
  );

  const evidenceType = searchParams.get("evidence_type") || "";
  const page = Number(searchParams.get("page") || "1");

  const { data: evidenceData, isLoading: evLoading } = useQuery({
    queryKey: ["trust-evidence", orgId, evidenceType, page],
    queryFn: () => {
      const p = new URLSearchParams({ page: String(page), per_page: "20" });
      if (evidenceType) p.set("evidence_type", evidenceType);
      return apiWithAuth<{ data: EvidenceItem[]; meta: { total: number; has_more: boolean } }>(
        `/orgs/${orgId}/trust/evidence?${p}`,
      );
    },
    enabled: tab === "evidence",
  });

  const { data: casesData, isLoading: casesLoading } = useQuery({
    queryKey: ["trust-cases", orgId, page],
    queryFn: () =>
      apiWithAuth<{ data: AssuranceCase[]; meta: { total: number; has_more: boolean } }>(
        `/orgs/${orgId}/trust/cases?page=${page}&per_page=20`,
      ),
    enabled: tab === "cases",
  });

  const evidence = evidenceData?.data ?? [];
  const cases = casesData?.data ?? [];
  const isLoading = tab === "evidence" ? evLoading : casesLoading;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Evidence & Assurance Cases</h1>

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {(["evidence", "cases"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium border-b-2 ${
              tab === t
                ? "border-[hsl(var(--primary))] text-[hsl(var(--primary))]"
                : "border-transparent text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
            }`}
          >
            {t === "evidence" ? "Evidence Items" : "Assurance Cases"}
          </button>
        ))}
      </div>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}

      {/* Evidence Items Tab */}
      {tab === "evidence" && !isLoading && (
        <div className="space-y-4">
          {/* Filter */}
          <select
            value={evidenceType}
            onChange={(e) => {
              const p = new URLSearchParams(searchParams);
              if (e.target.value) p.set("evidence_type", e.target.value);
              else p.delete("evidence_type");
              p.set("page", "1");
              p.set("tab", "evidence");
              router.push(`/dashboard/orgs/${orgId}/trust/evidence?${p}`);
            }}
            className="rounded-md border px-3 py-1.5 text-sm bg-transparent"
          >
            <option value="">All Types</option>
            {Object.entries(TYPE_LABELS).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>

          {evidence.length === 0 ? (
            <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
              No evidence items found.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-lg border">
              <table className="w-full text-sm">
                <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                  <tr>
                    <th className="px-4 py-2 font-medium">Title</th>
                    <th className="px-4 py-2 font-medium">Type</th>
                    <th className="px-4 py-2 font-medium">Status</th>
                    <th className="px-4 py-2 font-medium">Version</th>
                    <th className="px-4 py-2 font-medium">Source</th>
                    <th className="px-4 py-2 font-medium">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {evidence.map((e) => (
                    <tr key={e.id} className="border-b last:border-0 hover:bg-[hsl(var(--secondary))]">
                      <td className="px-4 py-2 font-medium">{e.title}</td>
                      <td className="px-4 py-2">
                        <Badge label={TYPE_LABELS[e.evidence_type] || e.evidence_type} colors="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200" />
                      </td>
                      <td className="px-4 py-2">
                        <Badge label={e.status} colors={STATUS_COLORS[e.status] || ""} />
                      </td>
                      <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">v{e.version}</td>
                      <td className="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]">
                        {e.source_type?.replace(/_/g, " ") || "—"}
                      </td>
                      <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">
                        {new Date(e.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Cases Tab */}
      {tab === "cases" && !isLoading && (
        <div className="space-y-4">
          {cases.length === 0 ? (
            <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
              No assurance cases found.
            </div>
          ) : (
            cases.map((c) => (
              <div key={c.id} className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">{c.title}</h3>
                  <Badge label={c.status} colors={STATUS_COLORS[c.status] || ""} />
                </div>
                <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">{c.claim}</p>
                <p className="mt-2 text-xs text-[hsl(var(--muted-foreground))]">
                  {new Date(c.created_at).toLocaleDateString()}
                </p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
