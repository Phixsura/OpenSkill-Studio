"use client";

import { useParams } from "next/navigation";
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

export default function CohortMembersPage() {
  const { orgId, cohortId } = useParams<{ orgId: string; cohortId: string }>();
  const queryClient = useQueryClient();
  const [userId, setUserId] = useState("");
  const [role, setRole] = useState("learner");

  const { data, isLoading } = useQuery({
    queryKey: ["cohort-members", cohortId],
    queryFn: () =>
      apiWithAuth<{ data: CohortMember[]; meta: { total: number } }>(
        `/orgs/${orgId}/cohorts/${cohortId}/members`,
      ),
  });

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
  });

  const removeMutation = useMutation({
    mutationFn: (uid: string) =>
      apiWithAuth(`/orgs/${orgId}/cohorts/${cohortId}/members/${uid}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cohort-members", cohortId] });
    },
  });

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">Cohort Members</h1>

      {/* Add member form */}
      <div className="mb-6 flex gap-2">
        <input
          type="text"
          placeholder="User ID"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          className="flex-1 rounded border px-3 py-2 text-sm"
        />
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

      {isLoading ? (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
      ) : !data?.data.length ? (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">No members enrolled yet.</p>
      ) : (
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
      )}
    </div>
  );
}
