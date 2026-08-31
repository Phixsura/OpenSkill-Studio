"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";
import { formatMinor } from "@/lib/cp";

interface BudgetPolicy {
  id: string;
  scope_type: string;
  scope_id: string | null;
  period: string;
  capability_key: string | null;
  usage_type: string | null;
  limit_minor: number;
  currency: string;
  warning_threshold_pct: number;
  hard_stop: boolean;
  is_active: boolean;
}

export default function TenantBudgetsPage() {
  const { tenantId } = useParams<{ tenantId: string }>();
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [scopeType, setScopeType] = useState("tenant");
  const [scopeId, setScopeId] = useState("");
  const [period, setPeriod] = useState("monthly");
  const [limitMajor, setLimitMajor] = useState("");
  const [hardStop, setHardStop] = useState(true);

  const budgetsQuery = useQuery({
    queryKey: ["tenant-budgets", tenantId],
    queryFn: () => apiWithAuth<{ data: BudgetPolicy[] }>(`/tenants/${tenantId}/budgets`),
  });
  const budgets = budgetsQuery.data?.data ?? [];

  const createMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/tenants/${tenantId}/budgets`, {
        method: "POST",
        body: JSON.stringify({
          scope_type: scopeType,
          scope_id: scopeType === "tenant" ? null : scopeId || null,
          period,
          limit_minor: Math.round(parseFloat(limitMajor) * 100),
          currency: "USD",
          hard_stop: hardStop,
        }),
      }),
    onSuccess: () => {
      toast.success("Budget created");
      setShowForm(false);
      setLimitMajor("");
      queryClient.invalidateQueries({ queryKey: ["tenant-budgets", tenantId] });
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Create failed"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth(`/tenants/${tenantId}/budgets/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      toast.success("Budget removed");
      queryClient.invalidateQueries({ queryKey: ["tenant-budgets", tenantId] });
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Delete failed"),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">AI spend budgets</h2>
        <Button onClick={() => setShowForm(!showForm)}>{showForm ? "Close" : "New budget"}</Button>
      </div>

      {showForm && (
        <div className="space-y-3 rounded-lg border p-4">
          <div className="grid gap-3 sm:grid-cols-4">
            <select
              className="rounded-md border bg-transparent px-3 py-2 text-sm"
              value={scopeType}
              onChange={(e) => setScopeType(e.target.value)}
            >
              <option value="tenant">Tenant-wide</option>
              <option value="org">Organization</option>
              <option value="project">Project</option>
              <option value="cohort">Cohort</option>
              <option value="user">User</option>
            </select>
            {scopeType !== "tenant" && (
              <Input
                placeholder={`${scopeType} ID`}
                value={scopeId}
                onChange={(e) => setScopeId(e.target.value)}
              />
            )}
            <select
              className="rounded-md border bg-transparent px-3 py-2 text-sm"
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
            >
              <option value="monthly">Monthly</option>
              <option value="daily">Daily</option>
            </select>
            <Input
              type="number"
              min="0"
              step="0.01"
              placeholder="Limit (USD)"
              value={limitMajor}
              onChange={(e) => setLimitMajor(e.target.value)}
            />
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={hardStop}
              onChange={(e) => setHardStop(e.target.checked)}
            />
            Hard stop (block consumption when exceeded; unchecked = warn only)
          </label>
          <Button
            onClick={() => createMutation.mutate()}
            disabled={!limitMajor || createMutation.isPending}
          >
            Create
          </Button>
        </div>
      )}

      {budgets.length === 0 ? (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          No budget policies. Your plan&apos;s AI budget entitlement still applies as a tenant-wide
          ceiling.
        </p>
      ) : (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full text-sm">
            <thead className="border-b bg-[hsl(var(--secondary))] text-left">
              <tr>
                <th className="px-4 py-2 font-medium">Scope</th>
                <th className="px-4 py-2 font-medium">Period</th>
                <th className="px-4 py-2 font-medium">Limit</th>
                <th className="px-4 py-2 font-medium">Mode</th>
                <th className="px-4 py-2" />
              </tr>
            </thead>
            <tbody>
              {budgets.map((b) => (
                <tr key={b.id} className="border-b last:border-0">
                  <td className="px-4 py-2">
                    {b.scope_type}
                    {b.scope_id && (
                      <span className="ml-1 font-mono text-xs text-[hsl(var(--muted-foreground))]">
                        {b.scope_id.slice(0, 10)}…
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2">{b.period}</td>
                  <td className="px-4 py-2 font-mono">{formatMinor(b.limit_minor, b.currency)}</td>
                  <td className="px-4 py-2">{b.hard_stop ? "hard stop" : "warn"}</td>
                  <td className="px-4 py-2 text-right">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteMutation.mutate(b.id)}
                      disabled={deleteMutation.isPending}
                    >
                      Remove
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
