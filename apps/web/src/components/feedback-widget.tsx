"use client";

import { useState } from "react";

const TYPES = [
  { value: "bug", icon: "🐛", label: "Bug" },
  { value: "feature", icon: "💡", label: "Feature" },
  { value: "improvement", icon: "✨", label: "Improvement" },
  { value: "praise", icon: "❤️", label: "Praise" },
];

interface FeedbackWidgetProps { onSubmit: (type: string, message: string) => void; }

export function FeedbackWidget({ onSubmit }: FeedbackWidgetProps) {
  const [open, setOpen] = useState(false);
  const [type, setType] = useState("bug");
  const [message, setMessage] = useState("");

  if (!open) return (
    <button onClick={() => setOpen(true)} className="fixed bottom-4 right-4 z-50 rounded-full bg-blue-600 p-3 text-white shadow-lg hover:bg-blue-700">
      💬
    </button>
  );

  return (
    <div className="fixed bottom-4 right-4 z-50 w-80 rounded-lg border bg-white p-4 shadow-xl dark:border-gray-700 dark:bg-gray-800">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-sm">Send Feedback</h3>
        <button onClick={() => setOpen(false)} className="text-gray-400">✕</button>
      </div>
      <div className="mt-2 flex gap-1">
        {TYPES.map(t => (
          <button key={t.value} onClick={() => setType(t.value)}
            className={`rounded px-2 py-1 text-xs ${type === t.value ? "bg-blue-100 font-semibold" : "text-gray-500"}`}>
            {t.icon} {t.label}
          </button>
        ))}
      </div>
      <textarea value={message} onChange={e => setMessage(e.target.value)} rows={3} placeholder="Describe your feedback..."
        className="mt-2 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
      <button onClick={() => { onSubmit(type, message); setMessage(""); setOpen(false); }} disabled={message.length < 5}
        className="mt-2 w-full rounded bg-blue-600 py-1.5 text-sm text-white disabled:opacity-50">Send</button>
    </div>
  );
}
