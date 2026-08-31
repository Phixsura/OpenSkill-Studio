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
    mutationFn: (d: Domain) =>
      apiWithAuth(`/tenants/${tenantId}/domains/${d.id}/verify`, {
        method: "POST",
        body: JSON.stringify({ token: verifyTokens[d.id] ?? "" }),
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
                        disabled={verifyMutation.isPending}
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
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
