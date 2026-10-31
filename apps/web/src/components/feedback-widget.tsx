"use client";
import { useState } from "react";

interface FeedbackWidgetProps { onSubmit: (reaction: string, comment: string) => void;
  submitted: boolean; }

const REACTIONS = [
  { key: "love", emoji: "😍", label: "Love it" },
  { key: "like", emoji: "👍", label: "Good" },
  { key: "meh", emoji: "😐", label: "OK" },
  { key: "dislike", emoji: "👎", label: "Needs work" },
];

export function FeedbackWidget({ onSubmit, submitted }: FeedbackWidgetProps) {
  const [selected, setSelected] = useState<string | null>(null);
  const [comment, setComment] = useState("");
  if (submitted) return <p className="text-sm text-green-600 text-center py-4">Thanks for your feedback! 🎉</p>;
  return (
    <div className="rounded-xl border p-4 dark:border-gray-700 max-w-sm">
      <p className="text-sm font-medium mb-2 text-center">How was this page?</p>
      <div className="flex justify-center gap-2 mb-3">
        {REACTIONS.map(r => (
          <button key={r.key} onClick={() => setSelected(r.key)} title={r.label}
            className={`text-2xl p-1 rounded-lg transition ${selected === r.key ? "bg-blue-100 dark:bg-blue-900/30 scale-110" : "hover:bg-gray-100 dark:hover:bg-gray-800"}`}>
            {r.emoji}
          </button>
        ))}
      </div>
      {selected && (
        <>
          <textarea value={comment} onChange={e => setComment(e.target.value)}
            placeholder="Any comments? (optional)" rows={2}
            className="w-full text-xs px-2 py-1 border rounded mb-2 dark:bg-gray-800 dark:border-gray-600" />
          <button onClick={() => onSubmit(selected, comment)}
            className="w-full py-1.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700">Submit</button>
        </>
      )}
    </div>
  );
}
