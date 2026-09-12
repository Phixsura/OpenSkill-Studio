"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Pager, QueryError } from "@/components/cp-list";
import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth, ApiError } from "@/lib/api";
import { formatMinor } from "@/lib/cp";
import { useImpersonation } from "@/lib/use-me";

interface OpsStatement {
  id: string;
  beneficiary_type: string;
  partner_id: string | null;
  partner_name: string | null;
  beneficiary_org_id: string | null;
  period: string;
  status: string;
  currency: string;
  share_total_minor: number;
  net_amount_minor: number;
  external_payment_ref: string | null;
}

export default function PlatformSettlementsPage() {
  const queryClient = useQueryClient();
  // R101[M27]: impersonation sessions are read-only server-side — disable the
  // settlement write controls instead of letting every click die with a 403.
  const impersonating = useImpersonation();
  const [genPartnerId, setGenPartnerId] = useState("");
  const [genPeriod, setGenPeriod] = useState("");
  const [payRefs, setPayRefs] = useState<Record<string, string>>({});
  const [page, setPage] = useState(1);

  const { data, isLoading, isError, error } = useQuery({
    // R101[M32]: page in key + sent to the API — the list truncated at the
    // backend default page size, hiding older unpaid statements entirely.
    queryKey: ["platform-settlements", page],
    queryFn: () =>
      apiWithAuth<{ data: OpsStatement[]; meta: { has_more: boolean } }>(
        `/platform/settlements?page=${page}&per_page=50`,
      ),
  });
  const statements = data?.data ?? [];

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["platform-settlements"] });

  const generateMutation = useMutation({
    mutationFn: () =>
      apiWithAuth("/platform/settlements/generate", {
        method: "POST",
        body: JSON.stringify({
          beneficiary_type: "partner",
          partner_id: genPartnerId,
          period: genPeriod,
        }),
      }),
    onSuccess: () => {
      toast.success("Statement generated");
      invalidate();
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Generate failed"),
  });

  const actionMutation = useMutation({
    mutationFn: ({ id, action, body }: { id: string; action: string; body?: unknown }) =>
      apiWithAuth(`/platform/settlements/${id}/${action}`, {
        method: "POST",
        body: body ? JSON.stringify(body) : "{}",
      }),
    onSuccess: () => {
      toast.success("Statement updated");
      invalidate();
    },
    onError: (e) => {
      toast.error(e instanceof ApiError ? e.message : "Action failed");
      // R101[L11]: a 409 means someone else already transitioned the statement —
      // refetch so the stale action buttons swap to the real current status.
      invalidate();
    },
  });

  return (
    <div className="space-y-6">
      <section className="space-y-2 rounded-lg border p-4">
        <h2 className="font-semibold">Generate statement</h2>
        <div className="flex flex-wrap gap-2">
          <Input
            className="max-w-xs"
            placeholder="Partner ID"
            value={genPartnerId}
            onChange={(e) => setGenPartnerId(e.target.value)}
          />
          <Input
            className="max-w-[10rem]"
            placeholder="Period (YYYY-MM)"
            value={genPeriod}
            onChange={(e) => setGenPeriod(e.target.value)}
          />
          <Button
            onClick={() => generateMutation.mutate()}
            disabled={!genPartnerId || !genPeriod || generateMutation.isPending || impersonating}
            title={impersonating ? "Read-only impersonation session" : undefined}
          >
            Generate
          </Button>
        </div>
      </section>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}
      {/* R101[M32]: query errors rendered as an empty table — an operator
          couldn't tell "no statements" from "the settlements endpoint is down". */}
      {isError && <QueryError error={error} what="settlements" />}
      {!isError && (
        <>
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Beneficiary</th>
                  <th className="px-4 py-2 font-medium">Period</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 text-right font-medium">Net</th>
                  <th className="px-4 py-2 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {statements.map((s) => (
                  <tr key={s.id} className="border-b last:border-0">
                    <td className="px-4 py-2">
                      {s.partner_name ?? s.beneficiary_org_id ?? s.partner_id ?? "—"}
                      <span className="ml-1 text-xs text-[hsl(var(--muted-foreground))]">
                        ({s.beneficiary_type})
                      </span>
                    </td>
                    <td className="px-4 py-2">{s.period}</td>
                    <td className="px-4 py-2">
                      <StatusBadge status={s.status} />
                    </td>
                    <td className="px-4 py-2 text-right font-mono">
                      {formatMinor(s.net_amount_minor, s.currency)}
                    </td>
                    <td className="px-4 py-2">
                      <div className="flex flex-wrap items-center gap-2">
                        {/* R101[L10]: double-clicking fired duplicate POSTs (the second
                            one 409s) — lock every action button while one is in flight. */}
                        {s.status === "draft" && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => actionMutation.mutate({ id: s.id, action: "finalize" })}
                            disabled={actionMutation.isPending || impersonating}
                            title={impersonating ? "Read-only impersonation session" : undefined}
                          >
                            Finalize
                          </Button>
                        )}
                        {s.status === "finalized" && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => actionMutation.mutate({ id: s.id, action: "approve" })}
                            disabled={actionMutation.isPending || impersonating}
                            title={impersonating ? "Read-only impersonation session" : undefined}
                          >
                            Approve
                          </Button>
                        )}
                        {s.status === "approved" && (
                          <>
                            <Input
                              className="h-8 max-w-[10rem] text-xs"
                              placeholder="Payment ref"
                              value={payRefs[s.id] ?? ""}
                              onChange={(e) => setPayRefs({ ...payRefs, [s.id]: e.target.value })}
                            />
                            <Button
                              size="sm"
                              onClick={() =>
                                actionMutation.mutate({
                                  id: s.id,
                                  action: "mark-paid",
                                  body: { external_payment_ref: payRefs[s.id] ?? "" },
                                })
                              }
                              disabled={!payRefs[s.id] || actionMutation.isPending || impersonating}
                              title={impersonating ? "Read-only impersonation session" : undefined}
                            >
                              Mark paid
                            </Button>
                          </>
                        )}
                        {s.external_payment_ref && (
                          <span className="font-mono text-xs text-[hsl(var(--muted-foreground))]">
                            {s.external_payment_ref}
                          </span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pager page={page} hasMore={data?.meta?.has_more ?? false} onPage={setPage} />
        </>
      )}
    </div>
  );
}
