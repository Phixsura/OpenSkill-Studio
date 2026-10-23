"use client";

import { useState } from "react";

interface FeedbackWidgetProps { onSubmit: (text: string, rating: number) => void; }

const emojis = ["😡", "😕", "😐", "😊", "🤩"];

export function FeedbackWidget({ onSubmit }: FeedbackWidgetProps) {
  const [rating, setRating] = useState(0);
  const [text, setText] = useState("");

  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="text-sm font-semibold mb-3">How was your experience?</h3>
      <div className="flex justify-center gap-3 mb-4">
        {emojis.map((emoji, i) => (
          <button key={i} onClick={() => setRating(i + 1)}
            className={`text-2xl transition ${rating === i + 1 ? "scale-125" : "opacity-40 hover:opacity-70"}`}>
            {emoji}
          </button>
        ))}
      </div>
      <textarea value={text} onChange={e => setText(e.target.value)}
        placeholder="Tell us more (optional)..." rows={3}
        className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
      <button onClick={() => { if (rating > 0) onSubmit(text, rating); }}
        disabled={rating === 0}
        className="mt-3 w-full rounded bg-blue-600 py-2 text-sm text-white disabled:opacity-30">Submit Feedback</button>
    </div>
  );
}
