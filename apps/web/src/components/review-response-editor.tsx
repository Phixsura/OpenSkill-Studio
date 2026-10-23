"use client";

import { useState } from "react";

interface Review { review_id: string; user_name: string; rating: number; text: string;
  has_response: boolean; response?: string; }
interface ReviewResponseEditorProps { review: Review;
  onSubmit: (reviewId: string, message: string) => void; }

export function ReviewResponseEditor({ review, onSubmit }: ReviewResponseEditorProps) {
  const [message, setMessage] = useState("");
  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-start gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-medium">{review.user_name}</span>
            <span className="text-xs text-yellow-500">{"★".repeat(review.rating)}{"☆".repeat(5 - review.rating)}</span>
          </div>
          <p className="mt-1 text-sm text-gray-500">{review.text}</p>
        </div>
      </div>
      {review.has_response && review.response ? (
        <div className="mt-3 rounded bg-blue-50 p-3 dark:bg-blue-900/10">
          <p className="text-xs text-gray-400">Your response:</p>
          <p className="text-sm">{review.response}</p>
        </div>
      ) : (
        <div className="mt-3 space-y-2">
          <textarea value={message} onChange={e => setMessage(e.target.value)}
            placeholder="Write a response..." rows={3}
            className="w-full rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400">{message.length}/2000</span>
            <button onClick={() => onSubmit(review.review_id, message)}
              disabled={message.length < 10}
              className="rounded bg-blue-600 px-4 py-1.5 text-sm text-white disabled:opacity-50">
              Reply
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
