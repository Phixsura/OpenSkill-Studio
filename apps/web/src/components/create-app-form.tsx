"use client";

import { useState } from "react";

interface CreateAppFormProps { categories: string[];
  onSubmit: (data: { name: string; slug: string; description: string; category: string }) => void; }

export function CreateAppForm({ categories, onSubmit }: CreateAppFormProps) {
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [desc, setDesc] = useState("");
  const [cat, setCat] = useState(categories[0] ?? "");

  const autoSlug = (n: string) => {
    setName(n);
    setSlug(n.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""));
  };

  return (
    <div className="mx-auto max-w-md space-y-4">
      <h2 className="text-lg font-bold">✨ Create New App</h2>
      <div>
        <label className="block text-xs text-gray-400 mb-1">App Name</label>
        <input value={name} onChange={e => autoSlug(e.target.value)} placeholder="My Cool App"
          className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
      </div>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Slug</label>
        <input value={slug} onChange={e => setSlug(e.target.value)}
          className="w-full rounded border px-3 py-2 text-sm font-mono dark:bg-gray-800 dark:border-gray-600" />
      </div>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Description</label>
        <textarea value={desc} onChange={e => setDesc(e.target.value)} rows={3}
          className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
      </div>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Category</label>
        <select value={cat} onChange={e => setCat(e.target.value)}
          className="w-full rounded border px-3 py-2 text-sm capitalize dark:bg-gray-800 dark:border-gray-600">
          {categories.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>
      <button onClick={() => onSubmit({ name, slug, description: desc, category: cat })}
        className="w-full rounded-lg bg-blue-600 py-2.5 text-sm font-medium text-white">Create App</button>
    </div>
  );
}
