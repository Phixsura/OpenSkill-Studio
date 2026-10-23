"use client";

import { useState } from "react";

interface ReviewReplyFormProps { reviewId: string; reviewerName: string; reviewText: string; rating: number; onSubmit: (body: string) => void; }

export function ReviewReplyForm({ reviewId, reviewerName, reviewText, rating, onSubmit }: ReviewReplyFormProps) {
  const [body, setBody] = useState("");

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 rounded bg-gray-50 p-3 dark:bg-gray-800">
        <div className="flex items-center gap-2">
          <span className="text-yellow-400">{"★".repeat(rating)}{"☆".repeat(5 - rating)}</span>
          <span className="text-sm font-medium">{reviewerName}</span>
        </div>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">{reviewText}</p>
      </div>
      <label className="block text-sm font-medium">Your Reply</label>
      <textarea value={body} onChange={e => setBody(e.target.value)} rows={3}
        placeholder="Thank the reviewer or address their feedback..."
        className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
      <div className="mt-2 flex items-center justify-between">
        <span className="text-xs text-gray-400">{body.length}/2000</span>
        <button onClick={() => { onSubmit(body); setBody(""); }} disabled={body.length < 10}
          className="rounded bg-blue-600 px-4 py-1.5 text-sm text-white disabled:opacity-50">Reply</button>
      </div>
    </div>
  );
}
