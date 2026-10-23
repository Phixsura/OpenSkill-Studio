"use client";

import { useState, useCallback } from "react";

interface DragDropUploaderProps { accept: string; maxSizeMb: number;
  onUpload: (files: File[]) => void; }

export function DragDropUploader({ accept, maxSizeMb, onUpload }: DragDropUploaderProps) {
  const [dragging, setDragging] = useState(false);
  const [files, setFiles] = useState<File[]>([]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const dropped = Array.from(e.dataTransfer.files);
    setFiles(prev => [...prev, ...dropped]);
    onUpload(dropped);
  }, [onUpload]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files ?? []);
    setFiles(prev => [...prev, ...selected]);
    onUpload(selected);
  }, [onUpload]);

  return (
    <div className="space-y-3">
      <div onDragOver={e => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)} onDrop={handleDrop}
        className={`flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed p-8 transition ${dragging ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "border-gray-300 dark:border-gray-600"}`}>
        <span className="text-3xl">📁</span>
        <p className="text-sm text-gray-500">Drag & drop files here or</p>
        <label className="cursor-pointer rounded bg-blue-600 px-4 py-1.5 text-sm text-white">
          Browse
          <input type="file" multiple accept={accept} onChange={handleChange} className="hidden" />
        </label>
        <p className="text-xs text-gray-400">Max {maxSizeMb}MB per file</p>
      </div>
      {files.length > 0 && (
        <div className="space-y-1">
          {files.map((f, i) => (
            <div key={i} className="flex items-center justify-between rounded border px-3 py-1.5 text-sm dark:border-gray-700">
              <span className="truncate">{f.name}</span>
              <span className="text-xs text-gray-400">{(f.size / 1024).toFixed(1)} KB</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
