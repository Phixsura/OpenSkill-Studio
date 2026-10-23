"use client";

import { useState } from "react";

interface ReviewFormProps { onSubmit: (data: { rating: number; title: string; body: string }) => void; }

export function ReviewForm({ onSubmit }: ReviewFormProps) {
  const [rating, setRating] = useState(0);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");

  return (
    <div className="space-y-4 rounded-lg border p-5 dark:border-gray-700">
      <h3 className="text-lg font-semibold">Write a Review</h3>
      <div>
        <p className="text-sm text-gray-400">Rating</p>
        <div className="mt-1 flex gap-1">
          {[1, 2, 3, 4, 5].map(star => (
            <button key={star} onClick={() => setRating(star)}
              className={`text-2xl ${star <= rating ? "text-yellow-400" : "text-gray-300"}`}>★</button>
          ))}
        </div>
      </div>
      <div>
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Review title"
          className="w-full rounded-lg border px-4 py-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
      </div>
      <div>
        <textarea value={body} onChange={e => setBody(e.target.value)} rows={4}
          placeholder="Share your experience with this app..."
          className="w-full rounded-lg border px-4 py-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
        <p className="mt-0.5 text-right text-xs text-gray-400">{body.length}/5000</p>
      </div>
      <button onClick={() => onSubmit({ rating, title, body })}
        disabled={rating === 0 || title.length < 5 || body.length < 20}
        className="w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white disabled:opacity-50">
        Submit Review
      </button>
    </div>
  );
}
