"use client";

import { useState } from "react";

const TYPES = ["bug", "feature_request", "question", "praise", "other"];
const TYPE_ICONS: Record<string, string> = { bug: "🐛", feature_request: "💡", question: "❓", praise: "⭐", other: "💬" };

interface FeedbackFormProps { onSubmit: (type: string, message: string) => void; }

export function FeedbackForm({ onSubmit }: FeedbackFormProps) {
  const [type, setType] = useState("");
  const [message, setMessage] = useState("");
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-3 font-semibold">💬 Send Feedback</h4>
      <div className="mb-3 flex flex-wrap gap-2">
        {TYPES.map(t => (
          <button key={t} onClick={() => setType(t)}
            className={`rounded-full border px-3 py-1 text-xs ${type === t ? "border-blue-500 bg-blue-50" : "border-gray-300"}`}>
            {TYPE_ICONS[t]} {t.replace(/_/g, " ")}
          </button>
        ))}
      </div>
      <textarea value={message} onChange={e => setMessage(e.target.value)} placeholder="Tell us what you think..."
        rows={3} className="mb-3 w-full rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800" />
      <button onClick={() => { if (type && message) onSubmit(type, message); }} disabled={!type || !message}
        className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50">Send</button>
    </div>
  );
}
