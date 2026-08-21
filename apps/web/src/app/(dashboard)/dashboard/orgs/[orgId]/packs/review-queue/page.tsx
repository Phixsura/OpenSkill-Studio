"use client";

import { toast } from "sonner";
import { useParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

interface Pack {
  id: string;
  name: string;
  slug: string;
  summary: string;
  status: string;
  visibility: string;
  review_status: string;
  install_count: number;
  created_at: string;
}

export default function ReviewQueuePage() {
  const { orgId } = useParams<{ orgId: string }>();
  const queryClient = useQueryClient();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["packs", orgId],
    queryFn: () =>
      apiWithAuth<{ data: Pack[] }>(`/orgs/${orgId}/packs?per_page=100`),
  });

  const pendingPacks = (data?.data ?? []).filter(
    (p) => p.review_status === "pending",
  );

  const approveMutation = useMutation({
    mutationFn: (packId: string) =>
      apiWithAuth(`/orgs/${orgId}/packs/${packId}/approve`, {
        method: "POST",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["packs", orgId] });
      toast.success("Pack approved");
    },
    onError: (err: Error) =>
      toast.error(err.message || "Failed to approve pack"),
  });

  const rejectMutation = useMutation({
    mutationFn: ({ packId, reason }: { packId: string; reason: string }) =>
      apiWithAuth(`/orgs/${orgId}/packs/${packId}/reject`, {
        method: "POST",
        body: JSON.stringify({ reason }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["packs", orgId] });
      toast.success("Pack rejected");
    },
    onError: (err: Error) =>
      toast.error(err.message || "Failed to reject pack"),
  });

  const handleReject = (packId: string) => {
    const reason = window.prompt("Rejection reason:");
    if (reason === null) return; // user cancelled
    if (!reason.trim()) {
      toast.error("A reason is required to reject a pack");
      return;
    }
    rejectMutation.mutate({ packId, reason: reason.trim() });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Review Queue</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Packs awaiting approval before publishing.
        </p>
      </div>

      {isError && (
        <p className="text-sm text-red-600">
          Failed to load packs. Please try again.
        </p>
      )}

      {isLoading && (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Loading...
        </p>
      )}

      {!isLoading && pendingPacks.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No packs pending review.
        </div>
      )}

      <div className="space-y-3">
        {pendingPacks.map((pack) => (
          <div
            key={pack.id}
            className="flex items-center justify-between rounded-lg border p-4"
          >
            <div>
              <h3 className="font-semibold">{pack.name}</h3>
              {pack.summary && (
                <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))] line-clamp-1">
                  {pack.summary}
                </p>
              )}
              <p className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">
                {new Date(pack.created_at).toLocaleDateString()}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                onClick={() => approveMutation.mutate(pack.id)}
                disabled={
                  approveMutation.isPending || rejectMutation.isPending
                }
              >
                Approve
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="text-red-600 hover:bg-red-50"
                onClick={() => handleReject(pack.id)}
                disabled={
                  approveMutation.isPending || rejectMutation.isPending
                }
              >
                Reject
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
