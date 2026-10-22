"use client";

import { useState } from "react";

interface TagInputProps { tags: string[]; onChange: (tags: string[]) => void; maxTags?: number; }

export function TagInput({ tags, onChange, maxTags = 10 }: TagInputProps) {
  const [input, setInput] = useState("");

  const addTag = () => {
    const tag = input.trim().toLowerCase();
    if (tag && !tags.includes(tag) && tags.length < maxTags) {
      onChange([...tags, tag]);
      setInput("");
    }
  };

  const removeTag = (tag: string) => onChange(tags.filter(t => t !== tag));

  return (
    <div>
      <div className="mb-2 flex flex-wrap gap-1">
        {tags.map(tag => (
          <span key={tag} className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2 py-0.5 text-xs dark:bg-blue-900">
            {tag}
            <button onClick={() => removeTag(tag)} className="text-blue-500 hover:text-red-500">×</button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && (e.preventDefault(), addTag())}
          placeholder="Add tag..." disabled={tags.length >= maxTags}
          className="flex-1 rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800" />
        <button onClick={addTag} disabled={tags.length >= maxTags}
          className="rounded bg-blue-600 px-3 py-1 text-sm text-white disabled:opacity-50">Add</button>
      </div>
      <p className="mt-1 text-xs text-gray-400">{tags.length}/{maxTags} tags</p>
    </div>
  );
}
