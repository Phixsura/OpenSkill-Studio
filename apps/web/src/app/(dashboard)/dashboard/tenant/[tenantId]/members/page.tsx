"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";
import { formatDate } from "@/lib/cp";
import { useImpersonation } from "@/lib/use-me";

interface TenantMember {
  id: string;
  user_id: string;
  role: string;
  created_at: string;
}

export default function TenantMembersPage() {
  const { tenantId } = useParams<{ tenantId: string }>();
  const queryClient = useQueryClient();
  // R101[M27]: impersonation sessions are read-only server-side — disable the
  // membership write controls instead of letting every click die with a 403.
  const impersonating = useImpersonation();
  const [userId, setUserId] = useState("");
  const [role, setRole] = useState("billing_admin");

  const membersQuery = useQuery({
    queryKey: ["tenant-members", tenantId],
    queryFn: () => apiWithAuth<{ data: TenantMember[] }>(`/tenants/${tenantId}/members`),
  });
  const members = membersQuery.data?.data ?? [];

  const addMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/tenants/${tenantId}/members`, {
        method: "POST",
        body: JSON.stringify({ user_id: userId, role }),
      }),
    onSuccess: () => {
      toast.success("Member added");
      setUserId("");
      queryClient.invalidateQueries({ queryKey: ["tenant-members", tenantId] });
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Add failed"),
  });

  const removeMutation = useMutation({
    mutationFn: (memberId: string) =>
      apiWithAuth(`/tenants/${tenantId}/members/${memberId}`, { method: "DELETE" }),
    onSuccess: () => {
      toast.success("Member removed");
      queryClient.invalidateQueries({ queryKey: ["tenant-members", tenantId] });
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Remove failed"),
  });

  return (
    <div className="max-w-2xl space-y-6">
      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Add tenant member</h2>
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Tenant members manage billing and account settings — separate from organization
          membership.
        </p>
        <div className="flex flex-wrap gap-2">
          <Input
            className="max-w-xs"
            placeholder="User ID"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
          />
          <select
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={role}
            onChange={(e) => setRole(e.target.value)}
          >
            <option value="billing_admin">billing_admin</option>
            <option value="owner">owner</option>
          </select>
          <Button
            onClick={() => addMutation.mutate()}
            disabled={!userId || addMutation.isPending || impersonating}
            title={impersonating ? "Read-only impersonation session" : undefined}
          >
            Add
          </Button>
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Members</h2>
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full text-sm">
            <thead className="border-b bg-[hsl(var(--secondary))] text-left">
              <tr>
                <th className="px-4 py-2 font-medium">User</th>
                <th className="px-4 py-2 font-medium">Role</th>
                <th className="px-4 py-2 font-medium">Since</th>
                <th className="px-4 py-2" />
              </tr>
            </thead>
            <tbody>
              {members.map((m) => (
                <tr key={m.id} className="border-b last:border-0">
                  <td className="px-4 py-2 font-mono text-xs">{m.user_id}</td>
                  <td className="px-4 py-2">{m.role}</td>
                  <td className="px-4 py-2">{formatDate(m.created_at)}</td>
                  <td className="px-4 py-2 text-right">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => removeMutation.mutate(m.id)}
                      disabled={removeMutation.isPending || impersonating}
                      title={impersonating ? "Read-only impersonation session" : undefined}
                    >
                      Remove
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
