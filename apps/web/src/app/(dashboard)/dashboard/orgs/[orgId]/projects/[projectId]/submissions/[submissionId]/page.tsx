"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface SubmissionDetail {
  id: string;
  version: number;
  status: string;
  submitted_at: string | null;
  is_late: boolean;
  final_score: number | null;
  items: { id: string; deliverable_id: string; type: string; file_name: string | null; content: string | null }[];
  reviews: { id: string; reviewer_type: string; status: string; score: number | null; feedback: string | null; created_at: string }[];
}

export default function SubmissionDetailPage() {
  const { orgId, projectId, submissionId } = useParams<{
    orgId: string; projectId: string; submissionId: string;
  }>();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["submission", submissionId],
    queryFn: () =>
      apiWithAuth<{ data: SubmissionDetail }>(
        `/orgs/${orgId}/projects/${projectId}/submissions/${submissionId}`,
      ),
  });

  const sub = data?.data;
  if (isLoading) return <p className="text-[hsl(var(--muted-foreground))]">Loading...</p>;
  if (isError || !sub) return <p className="text-[hsl(var(--destructive))]">Failed to load submission.</p>;

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Submission v{sub.version}</h1>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            Status: <span className="capitalize font-medium">{sub.status.replace("_", " ")}</span>
            {sub.is_late && <span className="ml-2 text-yellow-600">(Late)</span>}
          </p>
        </div>
        {sub.final_score !== null && (
          <span className="text-3xl font-bold">{sub.final_score}</span>
        )}
      </div>

      {/* Files / Items */}
      <div>
        <h2 className="text-lg font-semibold">Deliverables</h2>
        <div className="mt-3 space-y-2">
          {sub.items.map((item) => (
            <div key={item.id} className="rounded-lg border p-3 text-sm">
              {item.type === "file" && (
                <span>📎 {item.file_name}</span>
              )}
              {item.type !== "file" && (
                <p className="text-[hsl(var(--muted-foreground))]">{item.content}</p>
              )}
            </div>
          ))}
          {sub.items.length === 0 && (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">No items uploaded.</p>
          )}
        </div>
      </div>

      {/* Reviews */}
      <div>
        <h2 className="text-lg font-semibold">Reviews</h2>
        <div className="mt-3 space-y-3">
          {sub.reviews.map((r) => (
            <div key={r.id} className="rounded-lg border p-4">
              <div className="flex items-center justify-between text-sm">
                <span>
                  {r.reviewer_type === "ai" ? "🤖 AI Review" : "👨‍🏫 Instructor Review"}
                </span>
                <span className="capitalize font-medium">{r.status.replace("_", " ")}</span>
              </div>
              {r.score !== null && (
                <p className="mt-1 text-lg font-bold">{r.score} pts</p>
              )}
              {r.feedback && (
                <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">{r.feedback}</p>
              )}
              <p className="mt-2 text-xs text-[hsl(var(--muted-foreground))]">
                {new Date(r.created_at).toLocaleString()}
              </p>
            </div>
          ))}
          {sub.reviews.length === 0 && (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">No reviews yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}
