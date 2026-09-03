"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth, ApiError } from "@/lib/api";
import { formatDate, majorToMinor } from "@/lib/cp";

interface PlatformTenantDetail {
  id: string;
  name: string;
  slug: string;
  status: string;
  account_type: string;
  currency: string;
  timezone: string;
  billing_email: string | null;
  partner_id: string | null;
  trial_ends_at: string | null;
  suspended_at: string | null;
  suspension_reason: string | null;
  created_at: string;
}

interface TenantOrgSummary {
  id: string;
  name: string;
  slug: string;
  status: string;
}

export default function PlatformTenantDetailPage() {
  const { tenantId } = useParams<{ tenantId: string }>();
  const queryClient = useQueryClient();
  const [suspendReason, setSuspendReason] = useState("");
  const [adjustAmount, setAdjustAmount] = useState("");
  const [adjustReason, setAdjustReason] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["platform-tenant", tenantId],
    queryFn: () =>
      apiWithAuth<{ data: { tenant: PlatformTenantDetail; organizations: TenantOrgSummary[] } }>(
        `/platform/tenants/${tenantId}`,
      ),
  });
  // Detail endpoint nests the tenant beside its organizations
  const tenant = data?.data?.tenant;
  const orgs = data?.data?.organizations ?? [];

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["platform-tenant", tenantId] });
    queryClient.invalidateQueries({ queryKey: ["platform-tenants"] });
  };

  const suspendMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/platform/tenants/${tenantId}/suspend`, {
        method: "POST",
        body: JSON.stringify({ reason: suspendReason }),
      }),
    onSuccess: () => {
      toast.success("Tenant suspended");
      setSuspendReason("");
      invalidate();
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Suspend failed"),
  });

  const reactivateMutation = useMutation({
    mutationFn: () => apiWithAuth(`/platform/tenants/${tenantId}/reactivate`, { method: "POST" }),
    onSuccess: () => {
      toast.success("Tenant reactivated");
      invalidate();
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Reactivate failed"),
  });

  const adjustMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/platform/tenants/${tenantId}/credits/adjust`, {
        method: "POST",
        body: JSON.stringify({
          // R101: minor-unit factor is per-currency (JPY/KRW = 1) — the
          // hardcoded *100 credited zero-decimal tenants 100x the intent.
          amount_minor: majorToMinor(adjustAmount, tenant?.currency ?? "USD"),
          currency: tenant?.currency ?? "USD",
          reason: adjustReason,
        }),
      }),
    onSuccess: () => {
      toast.success("Credit adjusted");
      setAdjustAmount("");
      setAdjustReason("");
      // R101[M22]: the ledger/balances views (tenant credits page, platform
      // detail) rendered stale money until manual reload.
      queryClient.invalidateQueries({ queryKey: ["tenant-credits", tenantId] });
      queryClient.invalidateQueries({ queryKey: ["tenant-credit-ledger", tenantId] });
      invalidate();
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Adjust failed"),
  });

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }
  if (!tenant) {
    return <p className="text-sm text-red-600">Failed to load tenant.</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-bold">{tenant.name}</h1>
        <StatusBadge status={tenant.status} />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Info label="Slug" value={tenant.slug} />
        <Info label="Type" value={tenant.account_type} />
        <Info label="Currency" value={tenant.currency} />
        <Info label="Created" value={formatDate(tenant.created_at)} />
        <Info label="Billing email" value={tenant.billing_email ?? "—"} />
        <Info label="Partner" value={tenant.partner_id ?? "—"} />
        <Info label="Trial ends" value={formatDate(tenant.trial_ends_at)} />
        <Info label="Timezone" value={tenant.timezone} />
      </div>

      {tenant.suspension_reason && (
        <p className="rounded-md border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-900 dark:border-red-800 dark:bg-red-950 dark:text-red-100">
          Suspended {formatDate(tenant.suspended_at)}: {tenant.suspension_reason}
        </p>
      )}

      <section className="space-y-3 rounded-lg border p-4">
        <h2 className="font-semibold">Lifecycle</h2>
        {/* R101[L18]: cancelled/archived cannot transition — hide both controls */}
        {["cancelled", "archived"].includes(tenant.status) ? (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            This tenant is {tenant.status} — no lifecycle actions available.
          </p>
        ) : tenant.status !== "suspended" ? (
          <div className="flex flex-wrap gap-2">
            <Input
              className="max-w-sm"
              placeholder="Suspension reason (required)"
              value={suspendReason}
              onChange={(e) => setSuspendReason(e.target.value)}
            />
            <Button
              variant="destructive"
              onClick={() => suspendMutation.mutate()}
              disabled={!suspendReason || suspendMutation.isPending}
            >
              Suspend
            </Button>
          </div>
        ) : (
          <Button
            onClick={() => reactivateMutation.mutate()}
            disabled={reactivateMutation.isPending}
          >
            Reactivate
          </Button>
        )}
      </section>

      <section className="space-y-3 rounded-lg border p-4">
        <h2 className="font-semibold">Credit adjustment</h2>
        <div className="flex flex-wrap gap-2">
          <Input
            className="max-w-[10rem]"
            type="number"
            step="0.01"
            placeholder={`Amount (${tenant.currency})`}
            value={adjustAmount}
            onChange={(e) => setAdjustAmount(e.target.value)}
          />
          <Input
            className="max-w-sm"
            placeholder="Reason (audited)"
            value={adjustReason}
            onChange={(e) => setAdjustReason(e.target.value)}
          />
          <Button
            onClick={() => adjustMutation.mutate()}
            disabled={!adjustAmount || !adjustReason || adjustMutation.isPending}
          >
            Apply
          </Button>
        </div>
        <p className="text-xs text-[hsl(var(--muted-foreground))]">
          Positive credits, negative debits. Every adjustment lands in the tenant&apos;s ledger and
          the audit log.
        </p>
      </section>

      <section className="space-y-3 rounded-lg border p-4">
        <h2 className="font-semibold">Organizations</h2>
        {orgs.length === 0 ? (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">No organizations.</p>
        ) : (
          <ul className="space-y-2">
            {orgs.map((o) => (
              <li key={o.id} className="flex items-center gap-3 text-sm">
                <span className="font-medium">{o.name}</span>
                <span className="font-mono text-xs text-[hsl(var(--muted-foreground))]">
                  {o.slug}
                </span>
                <StatusBadge status={o.status} />
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border p-3">
      <p className="text-xs text-[hsl(var(--muted-foreground))]">{label}</p>
      <p className="mt-1 truncate text-sm font-medium">{value}</p>
    </div>
  );
}
