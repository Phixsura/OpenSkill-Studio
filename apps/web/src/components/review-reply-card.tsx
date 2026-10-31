"use client";
import { useState } from "react";

interface Review { reviewId: string; userName: string; rating: number; comment: string; reply?: { content: string; editedAt?: number }; }

export function ReviewReplyCard({ review, onReply, onEdit }: {
  review: Review; onReply?: (reviewId: string, content: string) => void; onEdit?: (reviewId: string, content: string) => void;
}) {
  const [draft, setDraft] = useState(review.reply?.content || "");
  const [editing, setEditing] = useState(false);
  const stars = "★".repeat(review.rating) + "☆".repeat(5 - review.rating);

  return (
    <div className="border dark:border-gray-700 rounded-xl p-4 space-y-3">
      <div className="flex justify-between">
        <div>
          <span className="font-medium text-sm">{review.userName}</span>
          <span className="text-yellow-500 ml-2 text-sm">{stars}</span>
        </div>
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-400">{review.comment}</p>
      {review.reply && !editing ? (
        <div className="bg-blue-50 dark:bg-blue-900/10 rounded-lg p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs font-semibold text-blue-700 dark:text-blue-400">Developer Reply</span>
            <button onClick={() => setEditing(true)} className="text-xs text-gray-400">Edit</button>
          </div>
          <p className="text-sm">{review.reply.content}</p>
          {review.reply.editedAt ? <span className="text-xs text-gray-400">(edited)</span> : null}
        </div>
      ) : (
        <div className="space-y-2">
          <textarea value={draft} onChange={e => setDraft(e.target.value)} placeholder="Write a reply..."
            className="w-full border dark:border-gray-700 rounded-lg p-2 text-sm bg-transparent resize-none" rows={2} maxLength={2000} />
          <div className="flex gap-2">
            <button onClick={() => { (review.reply ? onEdit : onReply)?.(review.reviewId, draft); setEditing(false); }}
              className="text-xs bg-blue-500 text-white px-3 py-1 rounded-lg">{review.reply ? "Save" : "Reply"}</button>
            {editing && <button onClick={() => setEditing(false)} className="text-xs text-gray-400">Cancel</button>}
          </div>
        </div>
      )}
    </div>
  );
}
