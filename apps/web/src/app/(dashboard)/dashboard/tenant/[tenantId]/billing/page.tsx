"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth, ApiError } from "@/lib/api";
import { formatDate, formatMinor, type InvoiceSummary, type Subscription } from "@/lib/cp";

interface PlanCatalogEntry {
  key: string;
  name: string;
  prices: { currency: string; interval: string; amount_minor: number }[];
}

export default function TenantBillingPage() {
  const { tenantId } = useParams<{ tenantId: string }>();
  const queryClient = useQueryClient();
  const [changeOpen, setChangeOpen] = useState(false);

  const subQuery = useQuery({
    queryKey: ["tenant-subscription", tenantId],
    queryFn: () =>
      apiWithAuth<{ data: Subscription | { status: "none" } }>(`/tenants/${tenantId}/subscription`),
  });
  const invoicesQuery = useQuery({
    queryKey: ["tenant-invoices", tenantId],
    queryFn: () => apiWithAuth<{ data: InvoiceSummary[] }>(`/tenants/${tenantId}/invoices`),
  });

  const sub = subQuery.data?.data;
  const hasSub = sub != null && sub.status !== "none";
  const invoices = invoicesQuery.data?.data ?? [];

  const cancelMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/tenants/${tenantId}/subscription/cancel`, {
        method: "POST",
        body: JSON.stringify({ at_period_end: true }),
      }),
    onSuccess: () => {
      toast.success("Subscription will cancel at period end");
      queryClient.invalidateQueries({ queryKey: ["tenant-subscription", tenantId] });
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Cancel failed"),
  });

  return (
    <div className="space-y-8">
      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Subscription</h2>
          {hasSub && (
            <Button variant="outline" onClick={() => setChangeOpen(true)}>
              Change plan
            </Button>
          )}
        </div>
        {subQuery.isLoading && (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
        )}
        {!subQuery.isLoading && !hasSub && (
          <div className="rounded-lg border border-dashed p-8 text-center text-sm text-[hsl(var(--muted-foreground))]">
            No active subscription — you are on community defaults.
          </div>
        )}
        {hasSub && sub && "plan_key" in sub && (
          <div className="rounded-lg border p-4">
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-xl font-semibold capitalize">{sub.plan_key}</span>
              <StatusBadge status={sub.status} />
              {sub.cancel_at_period_end && (
                <span className="text-xs text-amber-600">cancels at period end</span>
              )}
            </div>
            <div className="mt-3 grid gap-2 text-sm sm:grid-cols-3">
              <p>
                <span className="text-[hsl(var(--muted-foreground))]">Interval:</span>{" "}
                {sub.interval}
              </p>
              <p>
                <span className="text-[hsl(var(--muted-foreground))]">Seats reserved:</span>{" "}
                {sub.seat_quantity}
              </p>
              <p>
                <span className="text-[hsl(var(--muted-foreground))]">Current period:</span>{" "}
                {formatDate(sub.current_period_start)} – {formatDate(sub.current_period_end)}
              </p>
            </div>
            {!sub.cancel_at_period_end && (
              <Button
                variant="outline"
                className="mt-4"
                onClick={() => cancelMutation.mutate()}
                disabled={cancelMutation.isPending}
              >
                Cancel at period end
              </Button>
            )}
          </div>
        )}
        {changeOpen && (
          <PlanChangeDialog
            tenantId={tenantId}
            currentPlan={hasSub && sub && "plan_key" in sub ? sub.plan_key : null}
            onClose={() => setChangeOpen(false)}
          />
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Invoices</h2>
        {invoices.length === 0 ? (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">No invoices yet.</p>
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Number</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 font-medium">Issued</th>
                  <th className="px-4 py-2 font-medium">Total</th>
                  <th className="px-4 py-2 font-medium">Due</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv) => (
                  <tr key={inv.id} className="border-b last:border-0">
                    <td className="px-4 py-2">
                      <Link
                        href={`/dashboard/tenant/${tenantId}/billing/invoices/${inv.id}`}
                        className="font-mono text-xs underline-offset-2 hover:underline"
                      >
                        {inv.number ?? inv.id.slice(0, 10)}
                      </Link>
                    </td>
                    <td className="px-4 py-2">
                      <StatusBadge status={inv.status} />
                    </td>
                    <td className="px-4 py-2">{formatDate(inv.issued_at)}</td>
                    <td className="px-4 py-2">{formatMinor(inv.total_minor, inv.currency)}</td>
                    <td className="px-4 py-2">{formatMinor(inv.amount_due_minor, inv.currency)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

function PlanChangeDialog({
  tenantId,
  currentPlan,
  onClose,
}: {
  tenantId: string;
  currentPlan: string | null;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const [planKey, setPlanKey] = useState<string>("");
  const [preview, setPreview] = useState<Record<string, unknown> | null>(null);

  const plansQuery = useQuery({
    queryKey: ["plan-catalog"],
    queryFn: () => apiWithAuth<{ data: PlanCatalogEntry[] }>("/plans"),
  });
  const plans = (plansQuery.data?.data ?? []).filter((p) => p.key !== currentPlan);

  const previewMutation = useMutation({
    mutationFn: (key: string) =>
      apiWithAuth<{ data: Record<string, unknown> }>(
        `/tenants/${tenantId}/subscription/change-preview`,
        { method: "POST", body: JSON.stringify({ plan_key: key }) },
      ),
    onSuccess: (res) => setPreview(res.data),
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Preview failed"),
  });

  const changeMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/tenants/${tenantId}/subscription/change`, {
        method: "POST",
        body: JSON.stringify({ plan_key: planKey }),
      }),
    onSuccess: () => {
      toast.success("Plan change submitted");
      queryClient.invalidateQueries({ queryKey: ["tenant-subscription", tenantId] });
      queryClient.invalidateQueries({ queryKey: ["tenant-entitlements", tenantId] });
      onClose();
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Change failed"),
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-md space-y-4 rounded-lg border bg-[hsl(var(--card))] p-6">
        <h3 className="text-lg font-semibold">Change plan</h3>
        <select
          className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
          value={planKey}
          onChange={(e) => {
            setPlanKey(e.target.value);
            setPreview(null);
            if (e.target.value) previewMutation.mutate(e.target.value);
          }}
        >
          <option value="">Select a plan…</option>
          {plans.map((p) => (
            <option key={p.key} value={p.key}>
              {p.name}
            </option>
          ))}
        </select>
        {preview && (
          <pre className="max-h-48 overflow-auto rounded-md bg-[hsl(var(--secondary))] p-3 text-xs">
            {JSON.stringify(preview, null, 2)}
          </pre>
        )}
        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={() => changeMutation.mutate()}
            disabled={!planKey || changeMutation.isPending}
          >
            Confirm change
          </Button>
        </div>
      </div>
    </div>
  );
}
