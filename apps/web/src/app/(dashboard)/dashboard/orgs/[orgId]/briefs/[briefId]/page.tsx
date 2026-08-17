"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

interface ClientBrief {
  id: string;
  title: string;
  client_name: string;
  client_industry: string | null;
  project_type: string;
  objective: string;
  target_audience: string | null;
  tone_and_style: string | null;
  constraints: string | null;
  budget_range: string | null;
  timeline: string | null;
  deliverable_specs: Array<{ name?: string; type?: string; description?: string }>;
  evaluation_criteria: Array<Record<string, unknown>>;
  status: string;
  created_at: string;
}

export default function BriefDetailPage() {
  const { orgId, briefId } = useParams<{ orgId: string; briefId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [showConvert, setShowConvert] = useState(false);
  const [rubricCriterion, setRubricCriterion] = useState("Quality");
  const [rubricMaxScore, setRubricMaxScore] = useState("100");
  const [deadline, setDeadline] = useState("");

  const { data, isLoading, isError } = useQuery({
    queryKey: ["brief", briefId],
    queryFn: () =>
      apiWithAuth<{ data: ClientBrief }>(`/orgs/${orgId}/briefs/${briefId}`),
  });

  const convertMutation = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: { id: string } }>(
        `/orgs/${orgId}/briefs/${briefId}/convert`,
        {
          method: "POST",
          body: JSON.stringify({
            rubric: [
              {
                criterion: rubricCriterion,
                max_score: parseInt(rubricMaxScore, 10) || 100,
              },
            ],
            deadline: deadline || undefined,
          }),
        },
      ),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["brief", briefId] });
      router.push(`/dashboard/orgs/${orgId}/projects/${res.data.id}`);
    },
    onError: (err: Error) => alert(err.message || "Failed to convert brief"),
  });

  const brief = data?.data;

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading brief...</p>;
  }
  if (isError) {
    return <p className="text-sm text-red-600">Failed to load brief. It may not exist or you don&apos;t have access.</p>;
  }
  if (!brief) {
    return <p>Brief not found</p>;
  }

  return (
    <div>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{brief.title}</h1>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            {brief.client_name}
            {brief.client_industry && ` · ${brief.client_industry}`}
            {" · "}
            {brief.project_type.replace("_", " ")}
          </p>
        </div>
        <span className="rounded-full bg-[hsl(var(--secondary))] px-3 py-1 text-xs capitalize">
          {brief.status}
        </span>
      </div>

      {/* Brief details */}
      <div className="mb-8 space-y-4">
        <section>
          <h2 className="mb-1 text-sm font-semibold text-[hsl(var(--muted-foreground))]">
            Objective
          </h2>
          <p className="text-sm">{brief.objective}</p>
        </section>

        {brief.target_audience && (
          <section>
            <h2 className="mb-1 text-sm font-semibold text-[hsl(var(--muted-foreground))]">
              Target Audience
            </h2>
            <p className="text-sm">{brief.target_audience}</p>
          </section>
        )}

        {brief.tone_and_style && (
          <section>
            <h2 className="mb-1 text-sm font-semibold text-[hsl(var(--muted-foreground))]">
              Tone & Style
            </h2>
            <p className="text-sm">{brief.tone_and_style}</p>
          </section>
        )}

        {brief.constraints && (
          <section>
            <h2 className="mb-1 text-sm font-semibold text-[hsl(var(--muted-foreground))]">
              Constraints
            </h2>
            <p className="text-sm">{brief.constraints}</p>
          </section>
        )}

        {brief.deliverable_specs.length > 0 && (
          <section>
            <h2 className="mb-2 text-sm font-semibold text-[hsl(var(--muted-foreground))]">
              Deliverables
            </h2>
            <div className="space-y-1">
              {brief.deliverable_specs.map((spec, i) => (
                <div key={i} className="rounded border px-3 py-2 text-sm">
                  <span className="font-medium">{spec.name || `Deliverable ${i + 1}`}</span>
                  {spec.type && (
                    <span className="ml-2 text-xs text-[hsl(var(--muted-foreground))]">
                      ({spec.type})
                    </span>
                  )}
                  {spec.description && (
                    <p className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">
                      {spec.description}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        <div className="flex gap-6 text-xs text-[hsl(var(--muted-foreground))]">
          {brief.budget_range && <span>Budget: {brief.budget_range}</span>}
          {brief.timeline && <span>Timeline: {brief.timeline}</span>}
          <span>Created {new Date(brief.created_at).toLocaleDateString()}</span>
        </div>
      </div>

      {/* Convert to project */}
      {brief.status === "draft" && (
        <div>
          <Button onClick={() => setShowConvert(!showConvert)}>
            {showConvert ? "Cancel" : "Convert to Project →"}
          </Button>

          {showConvert && (
            <div className="mt-4 space-y-3 rounded border p-4">
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                This will create a new AI visual project from this brief. The brief&apos;s
                deliverable specs will become project deliverables.
              </p>
              <input
                type="text"
                placeholder="Rubric criterion name"
                value={rubricCriterion}
                onChange={(e) => setRubricCriterion(e.target.value)}
                className="w-full rounded border px-3 py-2 text-sm"
              />
              <input
                type="number"
                placeholder="Max score"
                value={rubricMaxScore}
                onChange={(e) => setRubricMaxScore(e.target.value)}
                className="w-32 rounded border px-3 py-2 text-sm"
              />
              <input
                type="datetime-local"
                placeholder="Deadline (optional)"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
                className="w-full rounded border px-3 py-2 text-sm"
              />
              <Button
                onClick={() => convertMutation.mutate()}
                disabled={convertMutation.isPending}
              >
                {convertMutation.isPending ? "Creating project..." : "Create Project"}
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
