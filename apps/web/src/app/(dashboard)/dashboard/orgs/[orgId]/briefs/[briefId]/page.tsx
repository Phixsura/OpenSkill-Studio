"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
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
  created_by: string;
  created_at: string;
}

interface BriefApplication {
  id: string;
  brief_id: string;
  user_id: string;
  status: string;
  note: string | null;
  applied_at: string;
  reviewed_at: string | null;
  user_name: string | null;
}

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  accepted: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
};

export default function BriefDetailPage() {
  const { orgId, briefId } = useParams<{ orgId: string; briefId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const currentUser = useAuthStore((s) => s.user);
  const [showConvert, setShowConvert] = useState(false);
  const [rubricCriterion, setRubricCriterion] = useState("Quality");
  const [rubricMaxScore, setRubricMaxScore] = useState("100");
  const [deadline, setDeadline] = useState("");
  const [applyNote, setApplyNote] = useState("");
  const [showEdit, setShowEdit] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editObjective, setEditObjective] = useState("");
  const [editTargetAudience, setEditTargetAudience] = useState("");
  const [editToneAndStyle, setEditToneAndStyle] = useState("");
  const [editConstraints, setEditConstraints] = useState("");
  const [editBudgetRange, setEditBudgetRange] = useState("");
  const [editTimeline, setEditTimeline] = useState("");

  const { data, isLoading, isError } = useQuery({
    queryKey: ["brief", briefId],
    queryFn: () =>
      apiWithAuth<{ data: ClientBrief }>(`/orgs/${orgId}/briefs/${briefId}`),
  });

  // Applications — visible to instructors, used to check if student already applied
  const { data: applicationsData } = useQuery({
    queryKey: ["brief-applications", briefId],
    queryFn: () =>
      apiWithAuth<{ data: BriefApplication[] }>(
        `/orgs/${orgId}/briefs/${briefId}/applications`,
      ).catch(() => ({ data: [] as BriefApplication[] })),
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

  const applyMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/briefs/${briefId}/apply`, {
        method: "POST",
        body: JSON.stringify({ note: applyNote || undefined }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["brief-applications", briefId] });
      setApplyNote("");
    },
    onError: (err: Error) => {
      if (err instanceof ApiError && err.status === 409) {
        alert("You have already applied to this brief.");
      } else {
        alert(err.message || "Failed to apply");
      }
    },
  });

  const reviewMutation = useMutation({
    mutationFn: ({ appId, status }: { appId: string; status: string }) =>
      apiWithAuth(
        `/orgs/${orgId}/briefs/${briefId}/applications/${appId}`,
        {
          method: "PUT",
          body: JSON.stringify({ status }),
        },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["brief-applications", briefId] });
    },
    onError: (err: Error) => alert(err.message || "Failed to review application"),
  });

  const editMutation = useMutation({
    mutationFn: (fields: Record<string, unknown>) =>
      apiWithAuth(`/orgs/${orgId}/briefs/${briefId}`, {
        method: "PUT",
        body: JSON.stringify(fields),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["brief", briefId] });
      setShowEdit(false);
    },
    onError: (err: Error) => alert(err.message || "Failed to update brief"),
  });

  const deleteMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/briefs/${briefId}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["briefs", orgId] });
      router.push(`/dashboard/orgs/${orgId}/briefs`);
    },
    onError: (err: Error) => alert(err.message || "Failed to delete brief"),
  });

  const brief = data?.data;
  const applications = applicationsData?.data || [];
  const myApplication = applications.find((a) => a.user_id === currentUser?.id);
  const isOwner = brief?.created_by === currentUser?.id;

  if (isLoading) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading brief...</p>;
  }
  if (isError) {
    return (
      <p className="text-sm text-red-600">
        Failed to load brief. It may not exist or you don&apos;t have access.
      </p>
    );
  }
  if (!brief) {
    return <p>Brief not found</p>;
  }

  const startEditing = () => {
    setEditTitle(brief.title);
    setEditObjective(brief.objective);
    setEditTargetAudience(brief.target_audience || "");
    setEditToneAndStyle(brief.tone_and_style || "");
    setEditConstraints(brief.constraints || "");
    setEditBudgetRange(brief.budget_range || "");
    setEditTimeline(brief.timeline || "");
    setShowEdit(true);
  };

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
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-[hsl(var(--secondary))] px-3 py-1 text-xs capitalize">
            {brief.status}
          </span>
          {isOwner && brief.status === "draft" && (
            <>
              <Button variant="outline" size="sm" onClick={startEditing}>
                Edit
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="text-red-600 hover:bg-red-50"
                onClick={() => {
                  if (confirm("Delete this brief? This cannot be undone.")) {
                    deleteMutation.mutate();
                  }
                }}
              >
                Delete
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Edit form */}
      {showEdit && (
        <div className="mb-6 space-y-3 rounded-lg border p-4">
          <h2 className="text-lg font-semibold">Edit Brief</h2>
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            placeholder="Title"
            className="w-full rounded border px-3 py-2 text-sm"
          />
          <textarea
            value={editObjective}
            onChange={(e) => setEditObjective(e.target.value)}
            placeholder="Objective"
            rows={3}
            className="w-full rounded border px-3 py-2 text-sm"
          />
          <input
            type="text"
            value={editTargetAudience}
            onChange={(e) => setEditTargetAudience(e.target.value)}
            placeholder="Target audience"
            className="w-full rounded border px-3 py-2 text-sm"
          />
          <input
            type="text"
            value={editToneAndStyle}
            onChange={(e) => setEditToneAndStyle(e.target.value)}
            placeholder="Tone & style"
            className="w-full rounded border px-3 py-2 text-sm"
          />
          <textarea
            value={editConstraints}
            onChange={(e) => setEditConstraints(e.target.value)}
            placeholder="Constraints"
            rows={2}
            className="w-full rounded border px-3 py-2 text-sm"
          />
          <div className="flex gap-3">
            <input
              type="text"
              value={editBudgetRange}
              onChange={(e) => setEditBudgetRange(e.target.value)}
              placeholder="Budget range"
              className="flex-1 rounded border px-3 py-2 text-sm"
            />
            <input
              type="text"
              value={editTimeline}
              onChange={(e) => setEditTimeline(e.target.value)}
              placeholder="Timeline"
              className="flex-1 rounded border px-3 py-2 text-sm"
            />
          </div>
          <div className="flex gap-2">
            <Button
              onClick={() =>
                editMutation.mutate({
                  title: editTitle,
                  objective: editObjective,
                  target_audience: editTargetAudience || undefined,
                  tone_and_style: editToneAndStyle || undefined,
                  constraints: editConstraints || undefined,
                  budget_range: editBudgetRange || undefined,
                  timeline: editTimeline || undefined,
                })
              }
              disabled={editMutation.isPending}
            >
              {editMutation.isPending ? "Saving..." : "Save Changes"}
            </Button>
            <Button variant="outline" onClick={() => setShowEdit(false)}>
              Cancel
            </Button>
          </div>
        </div>
      )}

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

      {/* Apply to Brief — only for open/active briefs */}
      {(brief.status === "open" || brief.status === "active") && (
        <div className="mb-8">
          {myApplication ? (
            <div className="rounded-lg border p-4">
              <p className="text-sm font-medium">
                ✓ You have applied
                <span
                  className={`ml-2 rounded-full px-2 py-0.5 text-xs capitalize ${STATUS_COLORS[myApplication.status] || ""}`}
                >
                  {myApplication.status}
                </span>
              </p>
              {myApplication.note && (
                <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
                  Your note: {myApplication.note}
                </p>
              )}
            </div>
          ) : (
            <div className="rounded-lg border p-4">
              <h3 className="mb-2 text-sm font-semibold">Apply to this Brief</h3>
              <textarea
                placeholder="Why do you want to work on this? (optional)"
                value={applyNote}
                onChange={(e) => setApplyNote(e.target.value)}
                rows={2}
                className="mb-2 w-full rounded border px-3 py-2 text-sm"
              />
              <Button
                onClick={() => applyMutation.mutate()}
                disabled={applyMutation.isPending}
                size="sm"
              >
                {applyMutation.isPending ? "Applying..." : "Apply"}
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Applications list — for instructors */}
      {applications.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-3 text-lg font-semibold">
            Applications ({applications.length})
          </h2>
          <div className="space-y-2">
            {applications.map((app) => (
              <div
                key={app.id}
                className="flex items-center justify-between rounded border px-4 py-3"
              >
                <div>
                  <span className="text-sm font-medium">
                    {app.user_name || app.user_id}
                  </span>
                  <span
                    className={`ml-2 rounded-full px-2 py-0.5 text-xs capitalize ${STATUS_COLORS[app.status] || ""}`}
                  >
                    {app.status}
                  </span>
                  {app.note && (
                    <p className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">
                      {app.note}
                    </p>
                  )}
                </div>
                {app.status === "pending" && (
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() =>
                        reviewMutation.mutate({ appId: app.id, status: "accepted" })
                      }
                      className="rounded bg-green-600 px-2 py-1 text-xs text-white hover:bg-green-700"
                    >
                      Accept
                    </button>
                    <button
                      type="button"
                      onClick={() =>
                        reviewMutation.mutate({ appId: app.id, status: "rejected" })
                      }
                      className="rounded bg-red-600 px-2 py-1 text-xs text-white hover:bg-red-700"
                    >
                      Reject
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

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
