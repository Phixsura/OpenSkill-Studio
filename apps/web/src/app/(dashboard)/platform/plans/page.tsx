"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth, ApiError } from "@/lib/api";
import { formatMinor } from "@/lib/cp";

interface PlanVersion {
  id: string;
  version: number;
  status: string;
  entitlements: Record<string, unknown>;
  prices: { currency: string; interval: string; amount_minor: number }[];
}

interface Plan {
  id: string;
  key: string;
  name: string;
  is_active: boolean;
  versions: PlanVersion[];
}

export default function PlatformPlansPage() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["platform-plans"],
    queryFn: () => apiWithAuth<{ data: Plan[] }>("/platform/plans"),
  });
  const plans = data?.data ?? [];

  const activateMutation = useMutation({
    mutationFn: (versionId: string) =>
      apiWithAuth(`/platform/plan-versions/${versionId}/activate`, { method: "POST" }),
    onSuccess: () => {
      toast.success("Version activated");
      queryClient.invalidateQueries({ queryKey: ["platform-plans"] });
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Activation failed"),
  });

  const newVersionMutation = useMutation({
    mutationFn: (planId: string) =>
      apiWithAuth(`/platform/plans/${planId}/versions`, { method: "POST", body: "{}" }),
    onSuccess: () => {
      toast.success("Draft version created (clones current active)");
      queryClient.invalidateQueries({ queryKey: ["platform-plans"] });
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Draft creation failed"),
  });

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }

  return (
    <div className="space-y-6">
      {plans.map((plan) => (
        <div key={plan.id} className="rounded-lg border p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-semibold">{plan.name}</h2>
              <span className="font-mono text-xs text-[hsl(var(--muted-foreground))]">
                {plan.key}
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => newVersionMutation.mutate(plan.id)}
              disabled={newVersionMutation.isPending}
            >
              New draft version
            </Button>
          </div>
          <div className="mt-3 space-y-2">
            {plan.versions.map((v) => (
              <div
                key={v.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-md border p-3"
              >
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium">v{v.version}</span>
                  <StatusBadge status={v.status} />
                  <span className="text-xs text-[hsl(var(--muted-foreground))]">
                    {v.prices
                      .map((p) => `${formatMinor(p.amount_minor, p.currency)}/${p.interval}`)
                      .join(" · ")}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <details className="text-xs">
                    <summary className="cursor-pointer text-[hsl(var(--muted-foreground))]">
                      entitlements
                    </summary>
                    <pre className="mt-2 max-h-48 max-w-md overflow-auto rounded bg-[hsl(var(--secondary))] p-2">
                      {JSON.stringify(v.entitlements, null, 2)}
                    </pre>
                  </details>
                  {v.status === "draft" && (
                    <Button
                      size="sm"
                      onClick={() => activateMutation.mutate(v.id)}
                      disabled={activateMutation.isPending}
                    >
                      Activate
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
