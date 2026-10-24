"use client";

import { useState } from "react";

interface ReviewFormProps { appName: string; isEdit: boolean; currentRating: number;
  currentTitle: string; currentBody: string;
  ratingLabels: Record<number, string>;
  onSubmit: (rating: number, title: string, body: string) => void; }

export function ReviewForm({ appName, isEdit, currentRating, currentTitle, currentBody,
  ratingLabels, onSubmit }: ReviewFormProps) {
  const [rating, setRating] = useState(currentRating);
  const [title, setTitle] = useState(currentTitle);
  const [body, setBody] = useState(currentBody);

  return (
    <div className="mx-auto max-w-md space-y-4">
      <h2 className="text-lg font-bold">{isEdit ? "Edit" : "Write"} Review — {appName}</h2>
      <div>
        <p className="text-xs text-gray-400 mb-2">Rating</p>
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map(n => (
            <button key={n} onClick={() => setRating(n)}
              className={`text-2xl transition ${n <= rating ? "text-yellow-500" : "text-gray-300"}`}>★</button>
          ))}
          {rating > 0 && <span className="ml-2 text-sm text-gray-400 self-center">{ratingLabels[rating]}</span>}
        </div>
      </div>
      <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Review title"
        className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
      <textarea value={body} onChange={e => setBody(e.target.value)} placeholder="Write your review..."
        rows={4} className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
      <button onClick={() => rating > 0 && title.trim() && onSubmit(rating, title, body)}
        disabled={rating === 0 || !title.trim()}
        className="w-full rounded-lg bg-blue-600 py-2.5 text-sm text-white disabled:opacity-30">
        {isEdit ? "Update Review" : "Submit Review"}
      </button>
    </div>
  );
}
