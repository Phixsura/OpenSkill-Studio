"use client";

import { useState } from "react";

interface ReviewFormV2Props { appName: string; onSubmit: (review: { rating: number; title: string; body: string; pros: string[]; cons: string[] }) => void; }

export function ReviewFormV2({ appName, onSubmit }: ReviewFormV2Props) {
  const [rating, setRating] = useState(0);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [pros, setPros] = useState("");
  const [cons, setCons] = useState("");

  const handleSubmit = () => {
    onSubmit({
      rating, title, body,
      pros: pros.split("\n").filter(Boolean),
      cons: cons.split("\n").filter(Boolean),
    });
  };

  return (
    <div className="rounded-lg border border-gray-200 p-6 dark:border-gray-700">
      <h2 className="text-lg font-semibold">Review {appName}</h2>
      <div className="mt-4">
        <label className="block text-sm font-medium">Rating</label>
        <div className="mt-1 flex gap-1">
          {[1, 2, 3, 4, 5].map(s => (
            <button key={s} onClick={() => setRating(s)} className={`text-2xl ${s <= rating ? "text-yellow-400" : "text-gray-300"}`}>★</button>
          ))}
        </div>
      </div>
      <div className="mt-3">
        <label className="block text-sm font-medium">Title</label>
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Summarize your experience"
          className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
      </div>
      <div className="mt-3">
        <label className="block text-sm font-medium">Review</label>
        <textarea value={body} onChange={e => setBody(e.target.value)} rows={4} placeholder="Share your detailed experience..."
          className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
      </div>
      <div className="mt-3 grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-green-600">👍 Pros</label>
          <textarea value={pros} onChange={e => setPros(e.target.value)} rows={2} placeholder="One per line"
            className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
        </div>
        <div>
          <label className="block text-sm font-medium text-red-600">👎 Cons</label>
          <textarea value={cons} onChange={e => setCons(e.target.value)} rows={2} placeholder="One per line"
            className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
        </div>
      </div>
      <button onClick={handleSubmit} disabled={rating === 0 || !title || body.length < 20}
        className="mt-4 w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white disabled:opacity-50">Submit Review</button>
    </div>
  );
}
