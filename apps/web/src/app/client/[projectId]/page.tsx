"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/status-badge";
import { ApiError } from "@/lib/api";
import { portalApi, portalRole, portalToken } from "@/lib/client-portal";

interface Brief {
  title: string;
  client_name: string | null;
  objective: string | null;
  target_audience: string | null;
  deliverable_specs: unknown;
  tone_and_style: string | null;
  timeline: unknown;
  evaluation_criteria: unknown;
}

interface PortalItem {
  id: string;
  type: string;
  file_name: string | null;
  mime_type: string | null;
  content: string | null;
  version: number;
}

interface PortalSubmission {
  id: string;
  version: number;
  status: string;
  submitted_at: string | null;
  share_note: string | null;
  items: PortalItem[];
}

interface ApprovalRecord {
  id: string;
  action: string;
  version: number;
  comment: string | null;
  acted_by: string; // R101[M0]: backend serializes the label as acted_by
  created_at: string;
}

interface PortalComment {
  id: string;
  item_id: string;
  text: string;
  anchor_type: string;
  author: string | null;
  created_at: string;
}

/** R101[M2]: the comments channel (issue §30) had ZERO portal UI — clients
 * could neither read the team's client-visible comments nor write their own
 * outside the revision flow. Per-submission thread, global anchor. */
function CommentsThread({
  projectId,
  submissionId,
  itemId,
  onAuthError,
}: {
  projectId: string;
  submissionId: string;
  itemId: string;
  onAuthError: (e: unknown) => boolean;
}) {
  const queryClient = useQueryClient();
  const [text, setText] = useState("");
  const commentsQuery = useQuery({
    queryKey: ["portal-comments", projectId, submissionId],
    queryFn: () =>
      portalApi<{ data: PortalComment[] }>(
        `/client-portal/projects/${projectId}/submissions/${submissionId}/comments`,
      ),
    retry: false,
  });
  const comments = (commentsQuery.data?.data ?? []).filter((c) => c.item_id === itemId);
  const postMutation = useMutation({
    mutationFn: () =>
      portalApi(`/client-portal/projects/${projectId}/submissions/${submissionId}/comments`, {
        method: "POST",
        body: JSON.stringify({ item_id: itemId, text, anchor_type: "global" }),
      }),
    onSuccess: () => {
      setText("");
      queryClient.invalidateQueries({ queryKey: ["portal-comments", projectId, submissionId] });
    },
    onError: (e) => {
      if (!onAuthError(e)) toast.error(e instanceof ApiError ? e.message : "Comment failed");
    },
  });
  return (
    <details className="mt-2">
      <summary className="cursor-pointer text-xs text-[hsl(var(--muted-foreground))]">
        Comments ({comments.length})
      </summary>
      <div className="mt-2 space-y-2">
        {comments.map((c) => (
          <div key={c.id} className="rounded bg-[hsl(var(--secondary))] p-2 text-xs">
            <span className="font-medium">{c.author ?? "Client"}</span>{" "}
            <span className="text-[hsl(var(--muted-foreground))]">
              {new Date(c.created_at).toLocaleString()}
            </span>
            <p className="mt-1 whitespace-pre-wrap">{c.text}</p>
          </div>
        ))}
        <div className="flex gap-2">
          <input
            className="w-full rounded-md border bg-transparent px-2 py-1 text-xs"
            placeholder="Add a comment…"
            value={text}
            maxLength={5000}
            onChange={(e) => setText(e.target.value)}
          />
          <Button
            size="sm"
            variant="outline"
            onClick={() => postMutation.mutate()}
            disabled={!text.trim() || postMutation.isPending}
          >
            Post
          </Button>
        </div>
      </div>
    </details>
  );
}

export default function ClientProjectPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const role = portalRole();
  const [revisionComment, setRevisionComment] = useState("");
  const [revisionFor, setRevisionFor] = useState<string | null>(null);

  // No session → bounce to access page.
  // R101[M1]: a logged-in ClientPortalMember carries a product access token —
  // requiring the guest JWT made the member channel unreachable.
  useEffect(() => {
    if (typeof window !== "undefined" && !portalToken()) {
      router.replace("/client/access");
    }
  }, [router]);

  // R123: onAuthError fires once per errored query (brief/submissions/history
  // can all 401 together) — the FIRST call removes the guest JWT, so a second
  // call misread the session as member-based and bounced a GUEST to /login.
  // Latch the redirect so only the first classification wins.
  const authRedirected = useRef(false);
  const onAuthError = (e: unknown) => {
    if (e instanceof ApiError && e.status === 401) {
      if (authRedirected.current) return true;
      authRedirected.current = true;
      // R113[H3]: a MEMBER session (no guest JWT — the product access token
      // was used) must bounce to /login, not the access-code page: members
      // have no access code, so the old redirect stranded them in a loop.
      const hadGuestJwt = sessionStorage.getItem("client_portal_jwt") != null;
      sessionStorage.removeItem("client_portal_jwt");
      router.replace(
        hadGuestJwt
          ? "/client/access"
          : `/login?redirect=${encodeURIComponent(`/client/${projectId}`)}`,
      );
      return true;
    }
    return false;
  };

  const briefQuery = useQuery({
    queryKey: ["portal-brief", projectId],
    queryFn: () => portalApi<{ data: Brief }>(`/client-portal/projects/${projectId}/brief`),
    retry: false,
  });
  const submissionsQuery = useQuery({
    queryKey: ["portal-submissions", projectId],
    queryFn: () =>
      portalApi<{ data: PortalSubmission[] }>(`/client-portal/projects/${projectId}/submissions`),
    retry: false,
  });
  const historyQuery = useQuery({
    queryKey: ["portal-history", projectId],
    queryFn: () =>
      portalApi<{ data: ApprovalRecord[] }>(
        `/client-portal/projects/${projectId}/approval-history`,
      ),
    retry: false,
  });

  useEffect(() => {
    // R101[M4]: any of the three queries can be the first to see the expired
    // token — only submissions was wired, leaving a half-dead page.
    for (const err of [submissionsQuery.error, briefQuery.error, historyQuery.error]) {
      if (err && onAuthError(err)) return;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [submissionsQuery.error, briefQuery.error, historyQuery.error]);

  const submissions = submissionsQuery.data?.data ?? [];
  const history = historyQuery.data?.data ?? [];
  const brief = briefQuery.data?.data;
  const finalAccepted = history.some((h) => h.action === "final_accepted");

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["portal-submissions", projectId] });
    queryClient.invalidateQueries({ queryKey: ["portal-history", projectId] });
  };

  const revisionMutation = useMutation({
    mutationFn: (submissionId: string) =>
      portalApi(
        `/client-portal/projects/${projectId}/submissions/${submissionId}/request-revision`,
        {
          method: "POST",
          body: JSON.stringify({ comment: revisionComment }),
        },
      ),
    onSuccess: () => {
      toast.success("Revision requested — the team has been notified");
      setRevisionFor(null);
      setRevisionComment("");
      invalidate();
    },
    onError: (e) => {
      if (!onAuthError(e)) toast.error(e instanceof ApiError ? e.message : "Request failed");
    },
  });

  const approveMutation = useMutation({
    mutationFn: (submissionId: string) =>
      portalApi(`/client-portal/projects/${projectId}/submissions/${submissionId}/approve`, {
        method: "POST",
        body: "{}",
      }),
    onSuccess: () => {
      toast.success("Version approved");
      invalidate();
    },
    onError: (e) => {
      if (!onAuthError(e)) toast.error(e instanceof ApiError ? e.message : "Approve failed");
    },
  });

  const finalAcceptMutation = useMutation({
    mutationFn: (submissionId: string) =>
      portalApi(`/client-portal/projects/${projectId}/final-accept`, {
        method: "POST",
        body: JSON.stringify({ submission_id: submissionId }),
      }),
    onSuccess: () => {
      toast.success("Project finally accepted — thank you!");
      invalidate();
    },
    onError: (e) => {
      if (!onAuthError(e)) toast.error(e instanceof ApiError ? e.message : "Accept failed");
    },
  });

  const downloadItem = async (submissionId: string, itemId: string) => {
    try {
      const res = await portalApi<{ data: { download_url: string } }>(
        `/client-portal/projects/${projectId}/submissions/${submissionId}/items/${itemId}/download`,
      );
      // R101[M5]: window.open AFTER an await is popup-blocked in most
      // browsers (no user-gesture context) and its null return was ignored —
      // the button silently did nothing. A synthetic anchor click navigates
      // without popup rules.
      const a = document.createElement("a");
      a.href = res.data.download_url;
      a.target = "_blank";
      a.rel = "noopener";
      a.click();
    } catch (e) {
      if (!onAuthError(e)) toast.error("Download failed");
    }
  };

  return (
    <div className="space-y-8">
      {finalAccepted && (
        <div className="rounded-md border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-900 dark:border-green-800 dark:bg-green-950 dark:text-green-100">
          ✓ This project has been finally accepted.
        </div>
      )}

      {brief && (
        <section className="rounded-lg border p-6">
          <h1 className="text-2xl font-bold">{brief.title}</h1>
          {brief.client_name && (
            <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
              for {brief.client_name}
            </p>
          )}
          {brief.objective && <p className="mt-4 text-sm">{brief.objective}</p>}
          {brief.tone_and_style && (
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
              Tone &amp; style: {brief.tone_and_style}
            </p>
          )}
          {/* R101[L1]: the whitelisted client-facing fields were fetched but
              never rendered — the client saw a thinner brief than intended */}
          {brief.target_audience && (
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
              Audience: {brief.target_audience}
            </p>
          )}
          {brief.deliverable_specs != null && (
            <details className="mt-2 text-sm">
              <summary className="cursor-pointer text-[hsl(var(--muted-foreground))]">
                Deliverable specs
              </summary>
              <pre className="mt-1 overflow-auto rounded bg-[hsl(var(--secondary))] p-2 text-xs">
                {JSON.stringify(brief.deliverable_specs, null, 2)}
              </pre>
            </details>
          )}
          {brief.timeline != null && (
            <details className="mt-2 text-sm">
              <summary className="cursor-pointer text-[hsl(var(--muted-foreground))]">
                Timeline
              </summary>
              <pre className="mt-1 overflow-auto rounded bg-[hsl(var(--secondary))] p-2 text-xs">
                {JSON.stringify(brief.timeline, null, 2)}
              </pre>
            </details>
          )}
          {brief.evaluation_criteria != null && (
            <details className="mt-2 text-sm">
              <summary className="cursor-pointer text-[hsl(var(--muted-foreground))]">
                Evaluation criteria
              </summary>
              <pre className="mt-1 overflow-auto rounded bg-[hsl(var(--secondary))] p-2 text-xs">
                {JSON.stringify(brief.evaluation_criteria, null, 2)}
              </pre>
            </details>
          )}
        </section>
      )}

      <section>
        <h2 className="mb-3 text-lg font-semibold">Deliverables</h2>
        {submissionsQuery.isLoading && (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
        )}
        {submissionsQuery.isError && (
          <p className="text-sm text-red-600">
            Could not load deliverables — please retry or ask for a new link.
          </p>
        )}
        {!submissionsQuery.isLoading && !submissionsQuery.isError && submissions.length === 0 && (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Nothing has been shared for review yet.
          </p>
        )}
        <div className="space-y-4">
          {submissions.map((s) => (
            <div key={s.id} className="rounded-lg border p-4">
              <div className="flex flex-wrap items-center gap-3">
                <span className="font-semibold">Version {s.version}</span>
                <StatusBadge status={s.status.toLowerCase()} />
                {s.share_note && (
                  <span className="text-xs text-[hsl(var(--muted-foreground))]">
                    {s.share_note}
                  </span>
                )}
              </div>

              <div className="mt-3 grid gap-3 sm:grid-cols-2">
                {s.items.map((item) => (
                  <div key={item.id} className="rounded-md border p-3 text-sm">
                    <p className="font-medium">
                      {item.file_name ?? `${item.type} content`}
                      <span className="ml-2 text-xs text-[hsl(var(--muted-foreground))]">
                        {item.type}
                      </span>
                    </p>
                    {item.content && (
                      <details className="mt-1">
                        <summary className="cursor-pointer text-xs text-[hsl(var(--muted-foreground))]">
                          view content
                        </summary>
                        <p className="mt-1 whitespace-pre-wrap text-xs text-[hsl(var(--muted-foreground))]">
                          {item.content}
                        </p>
                      </details>
                    )}
                    {item.type === "file" && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="mt-2"
                        onClick={() => downloadItem(s.id, item.id)}
                      >
                        Download
                      </Button>
                    )}
                    <CommentsThread
                      projectId={projectId}
                      submissionId={s.id}
                      itemId={item.id}
                      onAuthError={onAuthError}
                    />
                  </div>
                ))}
              </div>

              {!finalAccepted && (
                <div className="mt-4 flex flex-wrap gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      // R101[L0]: one shared comment state across cards — a
                      // typed comment silently retargeted to another version
                      setRevisionFor(s.id);
                      setRevisionComment("");
                    }}
                  >
                    Request revision
                  </Button>
                  {role === "approver" && (
                    <>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => approveMutation.mutate(s.id)}
                        disabled={approveMutation.isPending}
                      >
                        Approve version
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => finalAcceptMutation.mutate(s.id)}
                        disabled={finalAcceptMutation.isPending}
                      >
                        Final accept
                      </Button>
                    </>
                  )}
                </div>
              )}

              {revisionFor === s.id && (
                <div className="mt-3 space-y-2">
                  <textarea
                    className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
                    rows={3}
                    placeholder="What should change?"
                    value={revisionComment}
                    onChange={(e) => setRevisionComment(e.target.value)}
                  />
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={() => revisionMutation.mutate(s.id)}
                      disabled={!revisionComment || revisionMutation.isPending}
                    >
                      Send request
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setRevisionFor(null)}>
                      Cancel
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {history.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-semibold">Decision history</h2>
          <ol className="space-y-2">
            {history.map((h) => (
              <li key={h.id} className="rounded-md border p-3 text-sm">
                <span className="font-medium">{h.action.replace(/_/g, " ")}</span> on version{" "}
                {h.version} by {h.acted_by}
                <span className="ml-2 text-xs text-[hsl(var(--muted-foreground))]">
                  {new Date(h.created_at).toLocaleString()}
                </span>
                {h.comment && (
                  <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">{h.comment}</p>
                )}
              </li>
            ))}
          </ol>
        </section>
      )}
    </div>
  );
}
