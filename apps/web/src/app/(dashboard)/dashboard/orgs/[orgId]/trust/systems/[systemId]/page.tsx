"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { apiWithAuth } from "@/lib/api";

interface AISystem {
  id: string;
  org_id: string;
  name: string;
  slug: string;
  description: string | null;
  system_type: string;
  lifecycle: string;
  risk_tier: string | null;
  owner_user_id: string;
  linked_entity_type: string | null;
  linked_entity_id: string | null;
  tags: string[];
  version: number;
  created_at: string;
  updated_at: string;
}

interface UseCase {
  id: string;
  system_id: string;
  use_type: string;
  title: string;
  description: string;
  affected_groups: string[];
  data_classes: string[];
  deployment_contexts: string[];
  regions: string[];
  created_at: string;
}

interface Assessment {
  id: string;
  version: number;
  status: string;
  weighted_score: string | null;
  effective_tier: string | null;
  assessed_by: string;
  reviewed_by: string | null;
  created_at: string;
}

const RISK_COLORS: Record<string, string> = {
  minimal: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  low: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  high: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  critical: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

const LIFECYCLE_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  intake: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  under_review: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  approved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  deployed: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
  monitoring: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
  paused: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  deprecated: "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300",
  retired: "bg-gray-300 text-gray-500 dark:bg-gray-700 dark:text-gray-400",
};

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  submitted: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  approved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  superseded: "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300",
};

// Lifecycle transitions from ADR-017
const VALID_TRANSITIONS: Record<string, string[]> = {
  draft: ["intake"],
  intake: ["under_review", "draft"],
  under_review: ["approved", "intake"],
  approved: ["deployed", "paused"],
  deployed: ["monitoring", "paused", "deprecated"],
  monitoring: ["paused", "deprecated"],
  paused: ["deployed", "monitoring", "deprecated", "retired"],
  deprecated: ["retired", "paused"],
  retired: [],
};

function Badge({ label, colors }: { label: string; colors: string }) {
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${colors}`}>
      {label.replace(/_/g, " ")}
    </span>
  );
}

export default function SystemDetailPage() {
  const { orgId, systemId } = useParams<{ orgId: string; systemId: string }>();
  const queryClient = useQueryClient();
  const base = `/dashboard/orgs/${orgId}/trust`;
  const [tab, setTab] = useState<"overview" | "uses" | "assessments">("overview");

  const { data: systemData, isLoading } = useQuery({
    queryKey: ["trust-system", orgId, systemId],
    queryFn: () => apiWithAuth<{ data: AISystem }>(`/orgs/${orgId}/trust/systems/${systemId}`),
  });

  const { data: usesData } = useQuery({
    queryKey: ["trust-uses", orgId, systemId],
    queryFn: () => apiWithAuth<{ data: UseCase[] }>(`/orgs/${orgId}/trust/systems/${systemId}/use-cases`),
    enabled: tab === "uses" || tab === "overview",
  });

  const { data: assessmentsData } = useQuery({
    queryKey: ["trust-assessments", orgId, systemId],
    queryFn: () =>
      apiWithAuth<{ data: Assessment[]; meta: { total: number } }>(
        `/orgs/${orgId}/trust/systems/${systemId}/assessments`,
      ),
    enabled: tab === "assessments" || tab === "overview",
  });

  const lifecycleMutation = useMutation({
    mutationFn: (lifecycle: string) =>
      apiWithAuth(`/orgs/${orgId}/trust/systems/${systemId}/lifecycle`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lifecycle }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["trust-system", orgId, systemId] });
      queryClient.invalidateQueries({ queryKey: ["trust-systems"] });
      toast.success("Lifecycle updated");
    },
    onError: (err: Error) => toast.error(err?.message || "Failed to update lifecycle"),
  });

  const system = systemData?.data;
  const useCases = usesData?.data ?? [];
  const assessments = assessmentsData?.data ?? [];

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (!system) {
    return <p className="text-sm text-red-600">System not found.</p>;
  }

  const transitions = VALID_TRANSITIONS[system.lifecycle] || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{system.name}</h1>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            {system.system_type.replace(/_/g, " ")} · v{system.version} · {system.slug}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge label={system.lifecycle} colors={LIFECYCLE_COLORS[system.lifecycle] || ""} />
          {system.risk_tier && (
            <Badge label={system.risk_tier} colors={RISK_COLORS[system.risk_tier] || ""} />
          )}
        </div>
      </div>

      {/* Lifecycle Actions */}
      {transitions.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <span className="text-sm text-[hsl(var(--muted-foreground))] self-center">Transition to:</span>
          {transitions.map((t) => (
            <button
              key={t}
              onClick={() => lifecycleMutation.mutate(t)}
              disabled={lifecycleMutation.isPending}
              className="rounded-md border px-3 py-1 text-sm hover:bg-[hsl(var(--secondary))] disabled:opacity-50"
            >
              {t.replace(/_/g, " ")}
            </button>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {(["overview", "uses", "assessments"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium border-b-2 ${
              tab === t
                ? "border-[hsl(var(--primary))] text-[hsl(var(--primary))]"
                : "border-transparent text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
            }`}
          >
            {t === "overview" ? "Overview" : t === "uses" ? "Use Cases" : "Risk Assessments"}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tab === "overview" && (
        <div className="space-y-6">
          {system.description && (
            <div>
              <h3 className="mb-1 text-sm font-medium text-[hsl(var(--muted-foreground))]">Description</h3>
              <p className="text-sm">{system.description}</p>
            </div>
          )}
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg border p-4">
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Risk Tier</p>
              <p className="mt-1 text-lg font-bold">{system.risk_tier?.replace(/_/g, " ") || "Unassessed"}</p>
            </div>
            <div className="rounded-lg border p-4">
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Use Cases</p>
              <p className="mt-1 text-lg font-bold">{useCases.length}</p>
            </div>
            <div className="rounded-lg border p-4">
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Assessments</p>
              <p className="mt-1 text-lg font-bold">{assessments.length}</p>
            </div>
          </div>
          {system.linked_entity_type && (
            <div>
              <h3 className="mb-1 text-sm font-medium text-[hsl(var(--muted-foreground))]">Linked Entity</h3>
              <p className="text-sm">
                {system.linked_entity_type.replace(/_/g, " ")} — <code className="text-xs">{system.linked_entity_id}</code>
              </p>
            </div>
          )}
          {system.tags.length > 0 && (
            <div>
              <h3 className="mb-1 text-sm font-medium text-[hsl(var(--muted-foreground))]">Tags</h3>
              <div className="flex flex-wrap gap-1">
                {system.tags.map((tag) => (
                  <span key={tag} className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {tab === "uses" && (
        <div className="space-y-4">
          {useCases.length === 0 ? (
            <div className="rounded-lg border border-dashed p-8 text-center text-[hsl(var(--muted-foreground))]">
              No use cases defined yet.
            </div>
          ) : (
            useCases.map((uc) => (
              <div key={uc.id} className="rounded-lg border p-4">
                <div className="flex items-center gap-2">
                  <Badge
                    label={uc.use_type}
                    colors={uc.use_type === "intended"
                      ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                      : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"}
                  />
                  <h3 className="font-medium">{uc.title}</h3>
                </div>
                <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">{uc.description}</p>
                {uc.affected_groups.length > 0 && (
                  <p className="mt-2 text-xs text-[hsl(var(--muted-foreground))]">
                    Affected: {uc.affected_groups.join(", ")}
                  </p>
                )}
                {uc.regions.length > 0 && (
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">
                    Regions: {uc.regions.join(", ")}
                  </p>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {tab === "assessments" && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <Link
              href={`${base}/systems/${systemId}/assess`}
              className="rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm text-[hsl(var(--primary-foreground))] hover:opacity-90"
            >
              New Assessment
            </Link>
          </div>
          {assessments.length === 0 ? (
            <div className="rounded-lg border border-dashed p-8 text-center text-[hsl(var(--muted-foreground))]">
              No risk assessments yet. Create one to classify this system&apos;s risk.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-lg border">
              <table className="w-full text-sm">
                <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                  <tr>
                    <th className="px-4 py-2 font-medium">Version</th>
                    <th className="px-4 py-2 font-medium">Status</th>
                    <th className="px-4 py-2 font-medium">Score</th>
                    <th className="px-4 py-2 font-medium">Risk Tier</th>
                    <th className="px-4 py-2 font-medium">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {assessments.map((a) => (
                    <tr key={a.id} className="border-b last:border-0">
                      <td className="px-4 py-2 font-medium">v{a.version}</td>
                      <td className="px-4 py-2">
                        <Badge label={a.status} colors={STATUS_COLORS[a.status] || ""} />
                      </td>
                      <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">
                        {a.weighted_score ?? "—"}
                      </td>
                      <td className="px-4 py-2">
                        {a.effective_tier ? (
                          <Badge label={a.effective_tier} colors={RISK_COLORS[a.effective_tier] || ""} />
                        ) : (
                          "—"
                        )}
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
        </div>
      )}
    </div>
  );
}
