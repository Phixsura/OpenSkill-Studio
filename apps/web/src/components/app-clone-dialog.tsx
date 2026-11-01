"use client";

import { useState } from "react";

interface AppCloneDialogProps { originalName: string; onClone: (name: string, slug: string) => void; onCancel: () => void; }

export function AppCloneDialog({ originalName, onClone, onCancel }: AppCloneDialogProps) {
  const [name, setName] = useState(`${originalName} (Copy)`);
  const [slug, setSlug] = useState("");
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-3 font-semibold">📋 Clone App</h4>
      <p className="mb-3 text-sm text-gray-500">Create a copy of <strong>{originalName}</strong></p>
      <div className="mb-2"><label className="text-xs text-gray-500">New Name</label>
        <input value={name} onChange={e => setName(e.target.value)} className="mt-1 w-full rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800" /></div>
      <div className="mb-3"><label className="text-xs text-gray-500">New Slug</label>
        <input value={slug} onChange={e => setSlug(e.target.value)} placeholder="my-app-copy" className="mt-1 w-full rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800" /></div>
      <div className="flex gap-2">
        <button onClick={onCancel} className="rounded border px-4 py-2 text-sm">Cancel</button>
        <button onClick={() => { if (name && slug) onClone(name, slug); }} disabled={!name || !slug}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50">Clone</button>
      </div>
    </div>
  );
}
