"use client";

import { useParams } from "next/navigation";
import { toast } from "sonner";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

interface CohortMember {
  id: string;
  user_id: string;
  role: string;
  joined_at: string;
  user_name: string | null;
  user_email: string | null;
}

interface OrgMember {
  id: string;
  user: {
    id: string;
    display_name: string;
    email: string;
  };
  role: string;
}

export default function CohortMembersPage() {
  const { orgId, cohortId } = useParams<{ orgId: string; cohortId: string }>();
  const queryClient = useQueryClient();
  const [userId, setUserId] = useState("");
  const [role, setRole] = useState("learner");

  const { data, isLoading, isError } = useQuery({
    queryKey: ["cohort-members", cohortId],
    queryFn: () =>
      apiWithAuth<{ data: CohortMember[]; meta: { total: number } }>(
        `/orgs/${orgId}/cohorts/${cohortId}/members`,
      ),
  });

  const { data: orgMembers } = useQuery({
    queryKey: ["org-members", orgId],
    queryFn: () =>
      apiWithAuth<{ data: OrgMember[] }>(`/orgs/${orgId}/members`),
  });

  const cohortMemberIds = new Set(data?.data.map((m) => m.user_id) || []);
  const availableMembers = (orgMembers?.data || []).filter(
    (m) => !cohortMemberIds.has(m.user.id),
  );

  const addMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/cohorts/${cohortId}/members`, {
        method: "POST",
        body: JSON.stringify({ user_id: userId, role }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cohort-members", cohortId] });
      setUserId("");
    },
    onError: (err: Error) => toast.error(err.message || "Failed to add member"),
  });

  const removeMutation = useMutation({
    mutationFn: (uid: string) =>
      apiWithAuth(`/orgs/${orgId}/cohorts/${cohortId}/members/${uid}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cohort-members", cohortId] });
    },
    onError: (err: Error) => toast.error(err.message || "Failed to remove member"),
  });

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">Cohort Members</h1>

      {/* Add member form */}
      <div className="mb-6 flex gap-2">
        <select
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          className="flex-1 rounded border px-3 py-2 text-sm"
        >
          <option value="">Select an org member...</option>
          {availableMembers.map((m) => (
            <option key={m.user.id} value={m.user.id}>
              {m.user.display_name} ({m.user.email})
            </option>
          ))}
        </select>
        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="rounded border px-3 py-2 text-sm"
        >
          <option value="learner">Learner</option>
          <option value="instructor">Instructor</option>
        </select>
        <Button
          onClick={() => addMutation.mutate()}
          disabled={!userId.trim() || addMutation.isPending}
        >
          Add
        </Button>
      </div>

      {isError && (
        <p className="mb-4 text-sm text-red-600">Failed to load members. Please try again.</p>
      )}

      {isLoading ? (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
      ) : !isError && !data?.data.length ? (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">No members enrolled yet.</p>
      ) : data?.data.length ? (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-xs text-[hsl(var(--muted-foreground))]">
              <th className="px-3 py-2">Name</th>
              <th className="px-3 py-2">Role</th>
              <th className="px-3 py-2">Joined</th>
              <th className="px-3 py-2" />
            </tr>
          </thead>
          <tbody>
            {data.data.map((m) => (
              <tr key={m.id} className="border-b">
                <td className="px-3 py-2">{m.user_name || m.user_id}</td>
                <td className="px-3 py-2">
                  <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs capitalize">
                    {m.role}
                  </span>
                </td>
                <td className="px-3 py-2 text-xs">
                  {new Date(m.joined_at).toLocaleDateString()}
                </td>
                <td className="px-3 py-2 text-right">
                  <button
                    type="button"
                    onClick={() => removeMutation.mutate(m.user_id)}
                    className="text-xs text-red-600 hover:underline"
                  >
                    Remove
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
    </div>
  );
}
