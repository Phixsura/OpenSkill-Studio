"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth, ApiError } from "@/lib/api";
import { formatMinor } from "@/lib/cp";

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
  const [genPartnerId, setGenPartnerId] = useState("");
  const [genPeriod, setGenPeriod] = useState("");
  const [payRefs, setPayRefs] = useState<Record<string, string>>({});

  const { data, isLoading } = useQuery({
    queryKey: ["platform-settlements"],
    queryFn: () => apiWithAuth<{ data: OpsStatement[] }>("/platform/settlements"),
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
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Action failed"),
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
            disabled={!genPartnerId || !genPeriod || generateMutation.isPending}
          >
            Generate
          </Button>
        </div>
      </section>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}
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
                    {s.status === "draft" && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => actionMutation.mutate({ id: s.id, action: "finalize" })}
                      >
                        Finalize
                      </Button>
                    )}
                    {s.status === "finalized" && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => actionMutation.mutate({ id: s.id, action: "approve" })}
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
                          disabled={!payRefs[s.id]}
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
    </div>
  );
}
