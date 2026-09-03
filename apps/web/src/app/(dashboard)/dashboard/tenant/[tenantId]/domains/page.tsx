"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth, ApiError } from "@/lib/api";

interface Domain {
  id: string;
  hostname: string;
  status: string;
  is_primary: boolean;
  failure_reason: string | null;
  verification_record: string;
  verification_token?: string;
}

export default function TenantDomainsPage() {
  const { tenantId } = useParams<{ tenantId: string }>();
  const queryClient = useQueryClient();
  const [hostname, setHostname] = useState("");
  // Raw verification token is shown ONCE at creation — held in memory only
  const [newDomain, setNewDomain] = useState<Domain | null>(null);
  const [verifyTokens, setVerifyTokens] = useState<Record<string, string>>({});

  const domainsQuery = useQuery({
    queryKey: ["tenant-domains", tenantId],
    queryFn: () => apiWithAuth<{ data: Domain[] }>(`/tenants/${tenantId}/domains`),
  });
  const domains = domainsQuery.data?.data ?? [];

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["tenant-domains", tenantId] });

  const createMutation = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: Domain }>(`/tenants/${tenantId}/domains`, {
        method: "POST",
        body: JSON.stringify({ hostname }),
      }),
    onSuccess: (res) => {
      setNewDomain(res.data);
      setHostname("");
      invalidate();
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Create failed"),
  });

  const verifyMutation = useMutation({
    // R101[M34]: trim before sending — pasted tokens routinely carry stray
    // whitespace, and each doomed attempt burns the 6-per-hour verify budget.
    mutationFn: (d: Domain) =>
      apiWithAuth(`/tenants/${tenantId}/domains/${d.id}/verify`, {
        method: "POST",
        body: JSON.stringify({ token: (verifyTokens[d.id] ?? "").trim() }),
      }),
    onSuccess: () => {
      toast.success("Domain verified");
      invalidate();
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Verification failed"),
  });

  const actionMutation = useMutation({
    mutationFn: ({ id, action }: { id: string; action: "activate" | "disable" }) =>
      apiWithAuth(`/tenants/${tenantId}/domains/${id}/${action}`, { method: "POST" }),
    onSuccess: () => {
      toast.success("Domain updated");
      invalidate();
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Action failed"),
  });

  // R101[M21]: with the token shown only once, a lost token left the domain
  // stuck in pending_verification forever — the DELETE route existed but was
  // unreachable, so there was no escape hatch to re-add the domain.
  const removeMutation = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth(`/tenants/${tenantId}/domains/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      toast.success("Domain removed");
      invalidate();
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Remove failed"),
  });

  return (
    <div className="space-y-6">
      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Add custom domain</h2>
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Three steps: add the hostname, prove ownership via a DNS TXT record, then activate.
        </p>
        <div className="flex max-w-md gap-2">
          <Input
            placeholder="academy.example.com"
            value={hostname}
            onChange={(e) => setHostname(e.target.value)}
          />
          <Button
            onClick={() => createMutation.mutate()}
            disabled={!hostname || createMutation.isPending}
          >
            Add
          </Button>
        </div>
        {newDomain?.verification_token && (
          <div className="space-y-2 rounded-md border border-amber-300 bg-amber-50 p-4 text-sm dark:border-amber-800 dark:bg-amber-950">
            <p className="font-medium">
              Create this DNS TXT record — the token is shown only once:
            </p>
            <p className="break-all font-mono text-xs">
              {newDomain.verification_record} TXT &quot;{newDomain.verification_token}&quot;
            </p>
            {/* R101[M21]: the token lives only in this component's state — a
                refresh loses it with no recovery path other than re-adding. */}
            <p className="text-xs text-[hsl(var(--muted-foreground))]">
              Copy it now — it is shown only once. If you lose it, disable this domain and add it
              again.
            </p>
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Domains</h2>
        {domains.length === 0 ? (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">No custom domains.</p>
        ) : (
          <div className="space-y-3">
            {domains.map((d) => (
              <div key={d.id} className="rounded-lg border p-4">
                <div className="flex flex-wrap items-center gap-3">
                  <span className="font-mono text-sm">{d.hostname}</span>
                  <StatusBadge status={d.status} />
                  {d.is_primary && (
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">primary</span>
                  )}
                </div>
                {d.failure_reason && (
                  <p className="mt-1 text-xs text-red-600">{d.failure_reason}</p>
                )}
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  {(d.status === "pending_verification" || d.status === "failed") && (
                    <>
                      <Input
                        className="max-w-xs"
                        placeholder="Verification token"
                        value={verifyTokens[d.id] ?? ""}
                        onChange={(e) =>
                          setVerifyTokens({ ...verifyTokens, [d.id]: e.target.value })
                        }
                      />
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => verifyMutation.mutate(d)}
                        // R101[M34]: empty/garbage submits burned the
                        // 6-per-hour verify rate limit — tokens are far longer
                        // than 8 chars, so gate obviously-invalid input here.
                        disabled={
                          verifyMutation.isPending || (verifyTokens[d.id] ?? "").trim().length < 8
                        }
                      >
                        Verify
                      </Button>
                    </>
                  )}
                  {d.status === "verified" && (
                    <Button
                      size="sm"
                      onClick={() => actionMutation.mutate({ id: d.id, action: "activate" })}
                      disabled={actionMutation.isPending}
                    >
                      Activate
                    </Button>
                  )}
                  {d.status === "active" && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => actionMutation.mutate({ id: d.id, action: "disable" })}
                      disabled={actionMutation.isPending}
                    >
                      Disable
                    </Button>
                  )}
                  {/* R101[M21]: escape hatch for a stuck pending domain — the
                      one-time token cannot be re-shown, so remove + re-add is
                      the only recovery. */}
                  {d.status !== "active" && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => removeMutation.mutate(d.id)}
                      disabled={removeMutation.isPending}
                    >
                      Remove
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
