"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Pager, QueryError } from "@/components/cp-list";
import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth, ApiError } from "@/lib/api";
import { formatDate, formatMinor, type InvoiceSummary, type Subscription } from "@/lib/cp";
import { useImpersonation } from "@/lib/use-me";

interface PlanCatalogEntry {
  key: string;
  name: string;
  prices: { currency: string; interval: string; amount_minor: number }[];
}

export default function TenantBillingPage() {
  const { tenantId } = useParams<{ tenantId: string }>();
  const queryClient = useQueryClient();
  // R101[M27]: impersonation sessions are read-only server-side — disable the
  // billing write controls instead of letting every click die with a 403 toast.
  const impersonating = useImpersonation();
  const [changeOpen, setChangeOpen] = useState(false);
  // R101[M11]: invoices ignored pagination meta — tenants with more than one
  // backend page of invoices silently lost the older ones.
  const [invoicePage, setInvoicePage] = useState(1);

  const subQuery = useQuery({
    queryKey: ["tenant-subscription", tenantId],
    queryFn: () =>
      apiWithAuth<{ data: Subscription | { status: "none" } }>(`/tenants/${tenantId}/subscription`),
  });
  const invoicesQuery = useQuery({
    queryKey: ["tenant-invoices", tenantId, invoicePage],
    queryFn: () =>
      apiWithAuth<{ data: InvoiceSummary[]; meta: { has_more: boolean } }>(
        `/tenants/${tenantId}/invoices?page=${invoicePage}&per_page=50`,
      ),
  });

  const sub = subQuery.data?.data;
  const hasSub = sub != null && sub.status !== "none";
  const invoices = invoicesQuery.data?.data ?? [];

  // R101[H10]: there was NO way to start a subscription from the UI — the
  // whole self-serve funnel dead-ended at "No active subscription".
  const plansQuery = useQuery({
    queryKey: ["public-plans"],
    queryFn: () => apiWithAuth<{ data: PlanCatalogEntry[] }>("/plans"),
    enabled: !subQuery.isLoading && !hasSub,
  });
  const subscribablePlans = (plansQuery.data?.data ?? []).filter((p) =>
    ["school", "growth", "enterprise", "oem"].includes(p.key),
  );
  const [subscribePlan, setSubscribePlan] = useState("");

  const subscribeMutation = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: { checkout_url?: string } }>(`/tenants/${tenantId}/subscription`, {
        method: "POST",
        body: JSON.stringify({
          plan_key: subscribePlan,
          interval: "month",
          provider: "mock",
        }),
      }),
    onSuccess: (res) => {
      if (res?.data?.checkout_url) {
        window.location.href = res.data.checkout_url;
        return;
      }
      toast.success("Subscription started");
      queryClient.invalidateQueries({ queryKey: ["tenant-subscription", tenantId] });
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Subscribe failed"),
  });

  // R101[M14]: un-cancel — the backend reactivate endpoint existed for
  // exactly this but was unreachable from the UI.
  const reactivateMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/tenants/${tenantId}/subscription/reactivate`, { method: "POST" }),
    onSuccess: () => {
      toast.success("Subscription reactivated");
      queryClient.invalidateQueries({ queryKey: ["tenant-subscription", tenantId] });
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Reactivate failed"),
  });

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
        {/* R101[M24]: a failed subscription fetch rendered the "No active
            subscription" funnel — offering a paying tenant a fresh subscribe. */}
        {subQuery.isError && <QueryError error={subQuery.error} what="subscription" />}
        {!subQuery.isLoading && !subQuery.isError && !hasSub && (
          <div className="space-y-3 rounded-lg border border-dashed p-8 text-center">
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              No active subscription — you are on community defaults.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-2">
              <select
                className="rounded-md border bg-transparent px-3 py-2 text-sm"
                value={subscribePlan}
                onChange={(e) => setSubscribePlan(e.target.value)}
              >
                <option value="">Choose a plan…</option>
                {subscribablePlans.map((p) => (
                  <option key={p.key} value={p.key}>
                    {p.name}
                  </option>
                ))}
              </select>
              <Button
                onClick={() => subscribeMutation.mutate()}
                disabled={!subscribePlan || subscribeMutation.isPending || impersonating}
                title={impersonating ? "Read-only impersonation session" : undefined}
              >
                {subscribeMutation.isPending ? "Starting…" : "Subscribe"}
              </Button>
            </div>
          </div>
        )}
        {hasSub && sub && "plan_key" in sub && (
          <div className="rounded-lg border p-4">
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-xl font-semibold capitalize">{sub.plan_key}</span>
              <StatusBadge status={sub.status} />
              {sub.cancel_at_period_end && (
                <>
                  <span className="text-xs text-amber-600">cancels at period end</span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => reactivateMutation.mutate()}
                    disabled={reactivateMutation.isPending || impersonating}
                    title={impersonating ? "Read-only impersonation session" : undefined}
                  >
                    Keep subscription
                  </Button>
                </>
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
                disabled={cancelMutation.isPending || impersonating}
                title={impersonating ? "Read-only impersonation session" : undefined}
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
            currency={hasSub && sub && "currency" in sub ? sub.currency : null}
            onClose={() => setChangeOpen(false)}
          />
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Invoices</h2>
        {/* R101[M11]: a failed invoices fetch rendered "No invoices yet." as an
            authoritative empty state. */}
        {invoicesQuery.isError && <QueryError error={invoicesQuery.error} what="invoices" />}
        {!invoicesQuery.isLoading && !invoicesQuery.isError && invoices.length === 0 && (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">No invoices yet.</p>
        )}
        {invoices.length > 0 && (
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
        <Pager
          page={invoicePage}
          hasMore={invoicesQuery.data?.meta?.has_more ?? false}
          onPage={setInvoicePage}
        />
      </section>
    </div>
  );
}

// R101[L9]: human-readable breakdown line for the proration preview — only
// the fields the backend is known to return, skipping any that are missing.
function formatPreviewDetail(preview: Record<string, unknown>, currency: string): string {
  const parts: string[] = [];
  if (typeof preview.credit_unused_old_minor === "number") {
    parts.push(`${formatMinor(preview.credit_unused_old_minor, currency)} credit for unused time`);
  }
  if (typeof preview.charge_new_remaining_minor === "number") {
    parts.push(`${formatMinor(preview.charge_new_remaining_minor, currency)} for the new plan`);
  }
  if (typeof preview.days_left === "number") {
    parts.push(`${preview.days_left} days left in period`);
  }
  return parts.join(" · ");
}

function PlanChangeDialog({
  tenantId,
  currentPlan,
  currency,
  onClose,
}: {
  tenantId: string;
  currentPlan: string | null;
  currency: string | null;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  // R101[M27]: plan change is a write — read-only impersonation must not confirm it.
  const impersonating = useImpersonation();
  const [planKey, setPlanKey] = useState<string>("");
  const [preview, setPreview] = useState<Record<string, unknown> | null>(null);
  // R101[M23]: rapid plan switching raced the previews — a slow response for
  // plan A could land after plan B's and display A's numbers under B.
  const previewPlanRef = useRef<string>("");

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
    onSuccess: (res, key) => {
      // R101[M23]: only accept the response for the plan still selected.
      if (key === previewPlanRef.current) setPreview(res.data);
    },
    onError: (e, key) => {
      if (key === previewPlanRef.current)
        toast.error(e instanceof ApiError ? e.message : "Preview failed");
    },
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
            previewPlanRef.current = e.target.value;
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
        {/* R101[L9]: the proration preview dumped raw JSON minor units at the
            user ("net_minor": 12345) — render a human summary when the known
            fields are present, keep the <pre> as the fallback. */}
        {preview &&
          (typeof preview.net_minor === "number" && currency ? (
            <div className="space-y-1 rounded-md bg-[hsl(var(--secondary))] p-3 text-sm">
              <p className="font-medium">
                Net change: {preview.net_minor >= 0 ? "+" : ""}
                {formatMinor(preview.net_minor, currency)}
              </p>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                {formatPreviewDetail(preview, currency)}
              </p>
            </div>
          ) : (
            <pre className="max-h-48 overflow-auto rounded-md bg-[hsl(var(--secondary))] p-3 text-xs">
              {JSON.stringify(preview, null, 2)}
            </pre>
          ))}
        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={() => changeMutation.mutate()}
            disabled={!planKey || changeMutation.isPending || impersonating}
            title={impersonating ? "Read-only impersonation session" : undefined}
          >
            Confirm change
          </Button>
        </div>
      </div>
    </div>
  );
}
