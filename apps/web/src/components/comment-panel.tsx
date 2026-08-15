"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";
import type { CommentRegion, ItemComment } from "@/components/annotated-media";

function fmtTime(ms: number): string {
  const s = Math.floor(ms / 1000);
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

interface CommentPanelProps {
  orgId: string;
  submissionId: string;
  itemId: string;
  comments: ItemComment[];
  onChanged: () => void;
  activeCommentId?: string | null;
  onSelectComment?: (id: string | null) => void;
  /** Pending region drawn on the image, to be attached to the next comment. */
  pendingRegion?: CommentRegion | null;
  onClearPendingRegion?: () => void;
  /** For video items: current playback time to anchor time comments. */
  currentTimeMs?: number | null;
  canComment: boolean;
}

/**
 * Threaded comment list + composer for one submission item.
 * Region pins ↔ list entries highlight bidirectionally; comments can be
 * marked complete (comment-as-task, Frame.io model).
 */
export function CommentPanel({
  orgId,
  submissionId,
  itemId,
  comments,
  onChanged,
  activeCommentId,
  onSelectComment,
  pendingRegion,
  onClearPendingRegion,
  currentTimeMs,
  canComment,
}: CommentPanelProps) {
  const [text, setText] = useState("");
  const [replyTo, setReplyTo] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [anchorTime, setAnchorTime] = useState(false);

  const itemComments = comments.filter((c) => c.item_id === itemId);
  const roots = itemComments.filter((c) => !c.parent_id);
  const repliesByRoot = new Map<string, ItemComment[]>();
  for (const c of itemComments) {
    if (c.parent_id) {
      const list = repliesByRoot.get(c.parent_id) ?? [];
      list.push(c);
      repliesByRoot.set(c.parent_id, list);
    }
  }
  const regionOrder = itemComments.filter((c) => c.anchor_type === "region" && c.region);

  const submit = async () => {
    if (!text.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const body: Record<string, unknown> = { item_id: itemId, text: text.trim() };
      if (replyTo) {
        body.parent_id = replyTo;
      } else if (pendingRegion) {
        body.anchor_type = "region";
        body.region = pendingRegion;
      } else if (anchorTime && currentTimeMs != null) {
        body.anchor_type = "time";
        body.timestamp_ms = Math.round(currentTimeMs);
      }
      await apiWithAuth(`/orgs/${orgId}/submissions/${submissionId}/comments`, {
        method: "POST",
        body: JSON.stringify(body),
      });
      setText("");
      setReplyTo(null);
      onClearPendingRegion?.();
      onChanged();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to post comment");
    } finally {
      setBusy(false);
    }
  };

  const toggleComplete = async (c: ItemComment) => {
    try {
      await apiWithAuth(`/orgs/${orgId}/comments/${c.id}/completed`, {
        method: "PUT",
        body: JSON.stringify({ completed: !c.completed }),
      });
      onChanged();
    } catch {
      // non-fatal
    }
  };

  const renderComment = (c: ItemComment, pinIndex: number | null, isReply = false) => (
    <div
      key={c.id}
      onClick={() => onSelectComment?.(c.id === activeCommentId ? null : c.id)}
      className={`cursor-pointer rounded-md border p-2 text-sm ${
        c.id === activeCommentId ? "border-blue-500 bg-blue-500/5" : ""
      } ${isReply ? "ml-6" : ""}`}
    >
      <div className="flex items-center gap-2">
        {pinIndex != null && (
          <span className="flex h-4 w-4 items-center justify-center rounded-full bg-amber-500 text-[10px] font-bold text-white">
            {pinIndex}
          </span>
        )}
        {c.anchor_type === "time" && c.timestamp_ms != null && (
          <span className="rounded bg-[hsl(var(--secondary))] px-1.5 py-0.5 font-mono text-[10px]">
            {fmtTime(c.timestamp_ms)}
            {c.duration_ms ? `–${fmtTime(c.timestamp_ms + c.duration_ms)}` : ""}
          </span>
        )}
        <span className={c.completed ? "text-[hsl(var(--muted-foreground))] line-through" : ""}>
          {c.text}
        </span>
      </div>
      <div className="mt-1 flex items-center gap-3 text-xs text-[hsl(var(--muted-foreground))]">
        <span>{new Date(c.created_at).toLocaleString()}</span>
        {canComment && !isReply && (
          <button
            type="button"
            className="hover:underline"
            onClick={(e) => {
              e.stopPropagation();
              setReplyTo(replyTo === c.id ? null : c.id);
            }}
          >
            {replyTo === c.id ? "Cancel reply" : "Reply"}
          </button>
        )}
        {canComment && (
          <button
            type="button"
            className="hover:underline"
            onClick={(e) => {
              e.stopPropagation();
              toggleComplete(c);
            }}
          >
            {c.completed ? "Reopen" : "Mark complete"}
          </button>
        )}
      </div>
    </div>
  );

  return (
    <div className="space-y-2" data-testid={`comment-panel-${itemId}`}>
      {roots.length > 0 && (
        <div className="space-y-1.5">
          {roots.map((c) => {
            const pinIndex =
              c.anchor_type === "region" ? regionOrder.findIndex((r) => r.id === c.id) + 1 : null;
            return (
              <div key={c.id}>
                {renderComment(c, pinIndex || null)}
                {(repliesByRoot.get(c.id) ?? []).map((r) => renderComment(r, null, true))}
              </div>
            );
          })}
        </div>
      )}

      {canComment && (
        <div className="space-y-1.5">
          {pendingRegion && !replyTo && (
            <p className="text-xs text-blue-600">
              📍 Region selected — this comment will be anchored to it.{" "}
              <button type="button" className="underline" onClick={onClearPendingRegion}>
                Clear
              </button>
            </p>
          )}
          {replyTo && <p className="text-xs text-[hsl(var(--muted-foreground))]">Replying…</p>}
          {currentTimeMs != null && !replyTo && !pendingRegion && (
            <label className="flex items-center gap-1.5 text-xs text-[hsl(var(--muted-foreground))]">
              <input
                type="checkbox"
                checked={anchorTime}
                onChange={(e) => setAnchorTime(e.target.checked)}
              />
              Anchor at {fmtTime(currentTimeMs)}
            </label>
          )}
          {error && <p className="text-xs text-red-600">{error}</p>}
          <div className="flex gap-2">
            <input
              className="block w-full rounded-md border bg-transparent px-3 py-1.5 text-sm"
              placeholder={replyTo ? "Write a reply…" : "Add a comment…"}
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  submit();
                }
              }}
            />
            <Button size="sm" onClick={submit} disabled={busy || !text.trim()}>
              {busy ? "…" : "Post"}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
