"use client";

import { useState } from "react";

interface Category { id: string; label: string; icon: string; description: string; }
interface FeedbackFormPageProps { categories: Category[];
  onSubmit: (data: { category: string; title: string; description: string }) => void; }

export function FeedbackFormPage({ categories, onSubmit }: FeedbackFormPageProps) {
  const [category, setCategory] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold">Send Feedback</h1>
        <p className="mt-1 text-sm text-gray-500">Help us improve the platform</p>
      </div>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {categories.map(c => (
          <button key={c.id} onClick={() => setCategory(c.id)}
            className={`rounded-lg border p-3 text-center text-sm ${category === c.id ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20" : "border-gray-200 dark:border-gray-700"}`}>
            <span className="text-xl">{c.icon}</span>
            <p className="mt-1 font-medium">{c.label}</p>
          </button>
        ))}
      </div>
      <div className="space-y-3">
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Title"
          className="w-full rounded-lg border px-4 py-2.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
        <textarea value={description} onChange={e => setDescription(e.target.value)} rows={4}
          placeholder="Describe your feedback in detail..."
          className="w-full rounded-lg border px-4 py-2.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
      </div>
      <button onClick={() => onSubmit({ category, title, description })}
        disabled={!category || title.length < 5 || description.length < 20}
        className="w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white disabled:opacity-50">
        Submit Feedback
      </button>
    </div>
  );
}
