"use client";

interface FileUploadZoneProps { category: string; maxMb: number;
  allowedExtensions: string[]; onUpload: (file: File) => void;
  uploading: boolean; lastResult: { valid: boolean; filename?: string; error?: string } | null; }

export function FileUploadZone({ category, maxMb, allowedExtensions, onUpload, uploading, lastResult }: FileUploadZoneProps) {
  return (
    <div className="rounded-xl border-2 border-dashed dark:border-gray-600 p-8 text-center">
      <p className="text-3xl mb-2">📁</p>
      <p className="text-sm font-medium mb-1">Upload {category}</p>
      <p className="text-xs text-gray-400 mb-4">
        {allowedExtensions.join(", ")} · Max {maxMb}MB
      </p>
      <label className={`inline-block px-4 py-2 text-sm rounded-lg cursor-pointer ${
        uploading ? "bg-gray-300 text-gray-500" : "bg-blue-600 text-white hover:bg-blue-700"
      }`}>
        {uploading ? "Uploading..." : "Choose File"}
        <input type="file" className="hidden" disabled={uploading}
          onChange={e => e.target.files?.[0] && onUpload(e.target.files[0])} />
      </label>
      {lastResult && (
        <p className={`text-xs mt-3 ${lastResult.valid ? "text-green-600" : "text-red-500"}`}>
          {lastResult.valid ? `✅ ${lastResult.filename} uploaded` : `❌ ${lastResult.error}`}
        </p>
      )}
    </div>
  );
}
