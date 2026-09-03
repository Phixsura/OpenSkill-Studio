"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth, ApiError } from "@/lib/api";

interface Blueprint {
  id: string;
  name: string;
  description: string | null;
  is_active: boolean;
}

interface ProvisionRun {
  id: string;
  blueprint_id: string | null;
  tenant_id: string | null;
  status: string;
  steps: { step: string; status: string; error: string | null }[];
  error: string | null;
}

export default function PartnerProvisionPage() {
  const { partnerId } = useParams<{ partnerId: string }>();
  const [blueprintId, setBlueprintId] = useState("");
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [runId, setRunId] = useState<string | null>(null);

  const blueprintsQuery = useQuery({
    queryKey: ["partner-blueprints", partnerId],
    queryFn: () => apiWithAuth<{ data: Blueprint[] }>(`/partners/${partnerId}/blueprints`),
  });
  // R101[L6]: inactive blueprints always fail at submit — hide them
  const blueprints = (blueprintsQuery.data?.data ?? []).filter((b) => b.is_active !== false);

  // Poll run status while it works through the step machine
  const runQuery = useQuery({
    queryKey: ["provision-run", partnerId, runId],
    queryFn: () =>
      apiWithAuth<{ data: ProvisionRun }>(`/partners/${partnerId}/provision-runs/${runId}`),
    enabled: runId != null,
    refetchInterval: (query) => {
      // R101[M19]: stop on terminal status AND on query error — an erroring
      // poll spun forever while freezing the panel on the last stale status.
      if (query.state.status === "error") return false;
      const status = query.state.data?.data.status;
      return status === "completed" || status === "failed" ? false : 2000;
    },
    retry: false,
  });
  const run = runQuery.data?.data;

  const provisionMutation = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: ProvisionRun }>(`/partners/${partnerId}/provision-runs`, {
        method: "POST",
        body: JSON.stringify({
          blueprint_id: blueprintId,
          name,
          slug,
          // R101[H7]: key covers EVERY parameter — the old `${partnerId}:${slug}`
          // key 409'd forever when the operator corrected the name/blueprint
          // for the same slug (divergence guard compares all params). An
          // identical resubmit still resumes (and re-enqueues a failed run).
          idempotency_key: `${partnerId}:${slug}:${blueprintId}:${name}`.slice(0, 120),
        }),
      }),
    onSuccess: (res) => {
      setRunId(res.data.id);
      toast.success("Provisioning started");
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Provision failed"),
  });

  return (
    <div className="max-w-2xl space-y-6">
      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Provision a branded tenant</h2>
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Pick a blueprint, name the customer, submit — the platform creates the tenant, org,
          branding, subscription and installs the configured packs. No learner data is ever copied.
        </p>
        <select
          className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
          value={blueprintId}
          onChange={(e) => setBlueprintId(e.target.value)}
        >
          <option value="">Select blueprint…</option>
          {blueprints.map((b) => (
            <option key={b.id} value={b.id}>
              {b.name}
            </option>
          ))}
        </select>
        <Input
          placeholder="Customer name (e.g. Example Education Group)"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <Input
          placeholder="Slug (e.g. example-education)"
          value={slug}
          onChange={(e) => setSlug(e.target.value)}
        />
        <Button
          onClick={() => provisionMutation.mutate()}
          disabled={!blueprintId || !name || !slug || provisionMutation.isPending}
        >
          Provision tenant
        </Button>
      </section>

      {run && (
        <section className="space-y-3 rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <h3 className="font-semibold">Provision run</h3>
            <StatusBadge status={run.status} />
          </div>
          <ol className="space-y-1 text-sm">
            {run.steps.map((s) => (
              <li key={s.step} className="flex items-center gap-2">
                <span
                  className={
                    s.status === "done"
                      ? "text-green-600"
                      : s.status === "failed"
                        ? "text-red-600"
                        : "text-[hsl(var(--muted-foreground))]"
                  }
                >
                  {s.status === "done" ? "✓" : s.status === "failed" ? "✗" : "…"}
                </span>
                <span className="font-mono text-xs">{s.step}</span>
                {s.error && <span className="text-xs text-red-600">{s.error}</span>}
              </li>
            ))}
          </ol>
          {run.status === "completed" && run.tenant_id && (
            <p className="text-sm text-green-700 dark:text-green-400">
              Tenant provisioned: <span className="font-mono">{run.tenant_id}</span>
            </p>
          )}
          {run.error && <p className="text-sm text-red-600">{run.error}</p>}
        </section>
      )}
    </div>
  );
}
