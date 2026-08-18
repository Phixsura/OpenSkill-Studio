"use client";

import { useParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

interface SkillAssignment {
  cohort_id: string;
  skill_id: string;
  assigned_at: string;
  skill_name: string | null;
}

interface OrgSkill {
  id: string;
  name: string;
  status: string;
}

export default function CohortSkillsPage() {
  const { orgId, cohortId } = useParams<{ orgId: string; cohortId: string }>();
  const queryClient = useQueryClient();

  const {
    data: assigned,
    isLoading: assignedLoading,
    isError: assignedError,
  } = useQuery({
    queryKey: ["cohort-skills", cohortId],
    queryFn: () =>
      apiWithAuth<{ data: SkillAssignment[] }>(
        `/orgs/${orgId}/cohorts/${cohortId}/skills`,
      ),
  });

  const { data: orgSkills } = useQuery({
    queryKey: ["org-skills", orgId],
    queryFn: () =>
      apiWithAuth<{ data: OrgSkill[] }>(`/orgs/${orgId}/skills?per_page=100`),
  });

  const assignedIds = new Set(assigned?.data.map((a) => a.skill_id) || []);
  const available = orgSkills?.data.filter((s) => !assignedIds.has(s.id)) || [];

  const assignMutation = useMutation({
    mutationFn: (skillId: string) =>
      apiWithAuth(`/orgs/${orgId}/cohorts/${cohortId}/skills`, {
        method: "POST",
        body: JSON.stringify({ skill_id: skillId }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cohort-skills", cohortId] });
    },
    onError: (err: Error) => alert(err.message || "Failed to assign skill"),
  });

  const unassignMutation = useMutation({
    mutationFn: (skillId: string) =>
      apiWithAuth(`/orgs/${orgId}/cohorts/${cohortId}/skills/${skillId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cohort-skills", cohortId] });
    },
    onError: (err: Error) => alert(err.message || "Failed to remove skill"),
  });

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">Assigned Skills</h1>

      {assignedLoading && (
        <p className="mb-4 text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
      )}
      {assignedError && (
        <p className="mb-4 text-sm text-red-600">Failed to load skills. Please try again.</p>
      )}

      {/* Currently assigned */}
      {!assignedLoading && !assignedError && assigned?.data.length ? (
        <div className="mb-8 space-y-2">
          {assigned.data.map((a) => (
            <div
              key={a.skill_id}
              className="flex items-center justify-between rounded border px-4 py-2"
            >
              <span className="text-sm font-medium">{a.skill_name || a.skill_id}</span>
              <button
                type="button"
                onClick={() => unassignMutation.mutate(a.skill_id)}
                className="text-xs text-red-600 hover:underline"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p className="mb-8 text-sm text-[hsl(var(--muted-foreground))]">
          No skills assigned to this cohort yet.
        </p>
      )}

      {/* Available skills to assign */}
      {available.length > 0 && (
        <div>
          <h2 className="mb-3 text-lg font-semibold">Available Skills</h2>
          <div className="space-y-2">
            {available.map((s) => (
              <div
                key={s.id}
                className="flex items-center justify-between rounded border px-4 py-2"
              >
                <span className="text-sm">{s.name}</span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => assignMutation.mutate(s.id)}
                  disabled={assignMutation.isPending}
                >
                  Assign
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
