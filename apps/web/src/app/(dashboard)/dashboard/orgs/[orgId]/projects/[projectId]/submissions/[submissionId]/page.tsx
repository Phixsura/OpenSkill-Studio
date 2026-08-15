"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import {
  AnnotatedImage,
  type CommentRegion,
  type ItemComment,
} from "@/components/annotated-media";
import { CommentPanel } from "@/components/comment-panel";
import { GenerationData, parseGenerationMeta } from "@/components/generation-data";
import { MediaPreview } from "@/components/media-preview";
import { PromptDisplay } from "@/components/prompt-display";
import { VersionCompare } from "@/components/version-compare";
import { VersionHistory } from "@/components/version-history";
import { apiWithAuth } from "@/lib/api";

interface SubItem {
  id: string;
  deliverable_id: string;
  type: string;
  file_name: string | null;
  mime_type: string | null;
  content: string | null;
  version: number;
  note: string | null;
  created_at: string;
}

interface SubmissionDetail {
  id: string;
  version: number;
  status: string;
  submitted_at: string | null;
  is_late: boolean;
  final_score: number | null;
  items: SubItem[];
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

  const { data: commentsData, refetch: refetchComments } = useQuery({
    queryKey: ["submission-comments", submissionId],
    queryFn: () =>
      apiWithAuth<{ data: ItemComment[] }>(`/orgs/${orgId}/submissions/${submissionId}/comments`),
  });
  const comments = commentsData?.data ?? [];
  const [activeCommentId, setActiveCommentId] = useState<string | null>(null);
  const [annotatingItem, setAnnotatingItem] = useState<string | null>(null);
  const [pendingRegion, setPendingRegion] = useState<{
    itemId: string;
    region: CommentRegion;
  } | null>(null);

  const sub = data?.data;
  if (isLoading) return <p className="text-[hsl(var(--muted-foreground))]">Loading...</p>;
  if (isError || !sub) return <p className="text-[hsl(var(--destructive))]">Failed to load submission.</p>;

  // Group items by deliverable, show latest version per group
  const byDeliverable = new Map<string, SubItem[]>();
  for (const item of sub.items ?? []) {
    const list = byDeliverable.get(item.deliverable_id) ?? [];
    list.push(item);
    byDeliverable.set(item.deliverable_id, list);
  }

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

      {/* Deliverables with previews + anchored feedback */}
      <div>
        <h2 className="text-lg font-semibold">Deliverables</h2>
        <div className="mt-3 space-y-3">
          {[...byDeliverable.entries()].map(([deliverableId, items]) => {
            const sorted = [...items].sort((a, b) => b.version - a.version);
            const latest = sorted[0];
            if (!latest) return null;
            return (
              <div key={deliverableId} className="rounded-lg border p-4">
                {latest.file_name && (
                  <div className="mb-2 flex items-center gap-2 text-sm">
                    <span className="font-medium">{latest.file_name}</span>
                    {latest.version > 1 && (
                      <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900 dark:text-blue-200">
                        v{latest.version}
                      </span>
                    )}
                  </div>
                )}

                {latest.type === "prompt" ? (
                  <PromptDisplay content={latest.content} />
                ) : latest.type === "file" ? (
                  <div className="space-y-2">
                    {latest.mime_type?.startsWith("image/") ? (
                      <div className="space-y-1.5">
                        <AnnotatedImage
                          downloadPath={`/orgs/${orgId}/submissions/${submissionId}/files/${latest.id}/download`}
                          fileName={latest.file_name}
                          comments={comments.filter((c) => c.item_id === latest.id)}
                          activeCommentId={activeCommentId}
                          onSelectComment={setActiveCommentId}
                          drawing={annotatingItem === latest.id}
                          onDrawRegion={(region) => {
                            setPendingRegion({ itemId: latest.id, region });
                            setAnnotatingItem(null);
                          }}
                        />
                        <button
                          type="button"
                          className={`rounded border px-2 py-0.5 text-xs ${
                            annotatingItem === latest.id
                              ? "border-blue-500 text-blue-600"
                              : "hover:bg-[hsl(var(--secondary))]"
                          }`}
                          onClick={() =>
                            setAnnotatingItem(annotatingItem === latest.id ? null : latest.id)
                          }
                        >
                          {annotatingItem === latest.id
                            ? "Drawing… drag on the image"
                            : "✏️ Annotate region"}
                        </button>
                      </div>
                    ) : (
                      <MediaPreview
                        downloadPath={`/orgs/${orgId}/submissions/${submissionId}/files/${latest.id}/download`}
                        mimeType={latest.mime_type}
                        fileName={latest.file_name}
                      />
                    )}
                    {(() => {
                      const gen = parseGenerationMeta(latest.content);
                      return gen ? <GenerationData meta={gen} /> : null;
                    })()}
                  </div>
                ) : latest.type === "markdown" ? (
                  <div className="prose prose-sm max-w-none dark:prose-invert">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {latest.content ?? ""}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap text-sm text-[hsl(var(--muted-foreground))]">
                    {latest.content}
                  </p>
                )}

                {latest.type === "file" && sorted.length > 1 && (
                  <div className="mt-2 flex flex-wrap items-start gap-2">
                    <VersionHistory
                      items={sorted}
                      downloadPath={(itemId) =>
                        `/orgs/${orgId}/submissions/${submissionId}/files/${itemId}/download`
                      }
                    />
                    <VersionCompare
                      items={sorted}
                      downloadPath={(itemId) =>
                        `/orgs/${orgId}/submissions/${submissionId}/files/${itemId}/download`
                      }
                    />
                  </div>
                )}

                <div className="mt-3">
                  <CommentPanel
                    orgId={orgId}
                    submissionId={submissionId}
                    itemId={latest.id}
                    comments={comments}
                    onChanged={() => refetchComments()}
                    activeCommentId={activeCommentId}
                    onSelectComment={setActiveCommentId}
                    pendingRegion={
                      pendingRegion?.itemId === latest.id ? pendingRegion.region : null
                    }
                    onClearPendingRegion={() => setPendingRegion(null)}
                    canComment
                  />
                </div>
              </div>
            );
          })}
          {(sub.items ?? []).length === 0 && (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">No items uploaded.</p>
          )}
        </div>
      </div>

      {/* Reviews */}
      <div>
        <h2 className="text-lg font-semibold">Reviews</h2>
        <div className="mt-3 space-y-3">
          {(sub.reviews ?? []).map((r) => (
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
          {(sub.reviews ?? []).length === 0 && (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">No reviews yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}
