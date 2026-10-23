"use client";

import { useState } from "react";

interface FileUploadZoneProps { category: string; maxSizeMb: number; allowedTypes: string[];
  onUpload: (file: { name: string; size: number }) => void; }

export function FileUploadZone({ category, maxSizeMb, allowedTypes, onUpload }: FileUploadZoneProps) {
  const [dragging, setDragging] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleFile = (name: string, size: number) => {
    setFileName(name);
    onUpload({ name, size });
  };

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium capitalize">{category} Upload</h3>
      <div
        onDragOver={e => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => { e.preventDefault(); setDragging(false);
          const f = e.dataTransfer.files[0]; if (f) handleFile(f.name, f.size); }}
        className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center transition-colors ${dragging ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "border-gray-300 dark:border-gray-600"}`}>
        <span className="text-3xl">📁</span>
        <p className="mt-2 text-sm text-gray-500">Drag & drop or click to upload</p>
        <p className="mt-1 text-xs text-gray-400">
          Max {maxSizeMb}MB · {allowedTypes.join(", ")}
        </p>
      </div>
      {fileName && (
        <p className="text-xs text-green-600">✅ {fileName} selected</p>
      )}
    </div>
  );
}
