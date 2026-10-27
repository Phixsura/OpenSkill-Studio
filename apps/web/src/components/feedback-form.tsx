"use client";
import { useState } from "react";

const categories = ["bug", "feature", "improvement", "praise", "other"];
const catIcons: Record<string, string> = { bug: "🐛", feature: "✨", improvement: "📈", praise: "🌟", other: "💬" };

export function FeedbackForm({ onSubmit }: { onSubmit?: (cat: string, msg: string, rating: number) => void }) {
  const [category, setCategory] = useState("feature");
  const [message, setMessage] = useState("");
  const [rating, setRating] = useState(0);

  return (
    <div className="space-y-3">
      <h3 className="font-bold text-sm">Send Feedback</h3>
      <div className="flex gap-1">
        {categories.map(c => (
          <button key={c} onClick={() => setCategory(c)}
            className={`text-xs px-2.5 py-1 rounded-full capitalize ${category === c ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
            {catIcons[c]} {c}
          </button>
        ))}
      </div>
      <textarea value={message} onChange={e => setMessage(e.target.value)} placeholder="Your feedback..."
        className="w-full border dark:border-gray-700 rounded-lg px-3 py-2 text-sm bg-transparent resize-none" rows={3} />
      <div className="flex items-center gap-1">
        <span className="text-xs text-gray-500 mr-1">Rating:</span>
        {[1, 2, 3, 4, 5].map(n => (
          <button key={n} onClick={() => setRating(n)} className="text-lg">
            {n <= rating ? "★" : "☆"}
          </button>
        ))}
      </div>
      <button onClick={() => { onSubmit?.(category, message, rating); setMessage(""); setRating(0); }}
        className="w-full bg-blue-500 text-white py-2 rounded-lg text-sm">Submit Feedback</button>
    </div>
  );
}
