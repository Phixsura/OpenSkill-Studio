"use client";

import { useState } from "react";

interface TagInputProps { tags: string[]; suggestions: string[];
  onAdd: (tag: string) => void; onRemove: (tag: string) => void; maxTags: number; }

export function TagInput({ tags, suggestions, onAdd, onRemove, maxTags }: TagInputProps) {
  const [input, setInput] = useState("");
  const filtered = input ? suggestions.filter(s => s.includes(input.toLowerCase()) && !tags.includes(s)) : [];

  const add = (tag: string) => {
    if (tag && tags.length < maxTags && !tags.includes(tag)) {
      onAdd(tag.toLowerCase());
      setInput("");
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-1.5">
        {tags.map(t => (
          <span key={t} className="flex items-center gap-1 rounded-full bg-blue-100 px-2.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
            {t}
            <button onClick={() => onRemove(t)} className="text-blue-400 hover:text-blue-600">×</button>
          </span>
        ))}
      </div>
      {tags.length < maxTags && (
        <div className="relative">
          <input value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && add(input)}
            placeholder="Add tag..." className="w-full rounded border px-3 py-1.5 text-sm dark:bg-gray-800 dark:border-gray-600" />
          {filtered.length > 0 && (
            <div className="absolute left-0 right-0 mt-1 rounded-lg border bg-white shadow dark:bg-gray-900 dark:border-gray-700 z-10">
              {filtered.map(s => (
                <button key={s} onClick={() => add(s)}
                  className="block w-full px-3 py-1.5 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800">{s}</button>
              ))}
            </div>
          )}
        </div>
      )}
      <p className="text-xs text-gray-400">{tags.length}/{maxTags} tags</p>
    </div>
  );
}
