"use client";
import { useState } from "react";

interface TagInputProps { tags: string[]; maxTags: number;
  onAdd: (tag: string) => void; onRemove: (tag: string) => void;
  suggestions?: string[]; }

export function TagInput({ tags, maxTags, onAdd, onRemove, suggestions = [] }: TagInputProps) {
  const [input, setInput] = useState("");
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && input.trim() && tags.length < maxTags) {
      onAdd(input.trim().toLowerCase());
      setInput("");
    }
  };
  return (
    <div className="rounded-xl border p-4 dark:border-gray-700">
      <div className="flex flex-wrap gap-1.5 mb-2">
        {tags.map(t => (
          <span key={t} className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-blue-100 dark:bg-blue-900/20 text-blue-700">
            {t}
            <button onClick={() => onRemove(t)} className="hover:text-red-500">×</button>
          </span>
        ))}
      </div>
      <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={handleKeyDown}
        placeholder={tags.length >= maxTags ? "Max tags reached" : "Add tag..."}
        disabled={tags.length >= maxTags}
        className="w-full text-sm px-2 py-1 border-0 outline-none bg-transparent" />
      <p className="text-xs text-gray-400 mt-1">{tags.length}/{maxTags} tags</p>
    </div>
  );
}
