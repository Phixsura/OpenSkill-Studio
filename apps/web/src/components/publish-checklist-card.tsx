"use client";

interface PublishChecklistCardProps { canPublish: boolean; errors: string[]; warnings: string[]; onPublish?: () => void; }

export function PublishChecklistCard({ canPublish, errors, warnings, onPublish }: PublishChecklistCardProps) {
  return (
    <div className={`rounded-lg border p-4 ${canPublish ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
      <h4 className="mb-2 font-semibold">{canPublish ? "✅ Ready to Publish" : "❌ Not Ready"}</h4>
      {errors.length > 0 && <ul className="mb-2 space-y-1">{errors.map((e, i) => <li key={i} className="text-sm text-red-600">❌ {e}</li>)}</ul>}
      {warnings.length > 0 && <ul className="mb-2 space-y-1">{warnings.map((w, i) => <li key={i} className="text-sm text-yellow-600">⚠️ {w}</li>)}</ul>}
      {canPublish && onPublish && <button onClick={onPublish} className="mt-2 w-full rounded bg-green-600 py-2 text-sm font-medium text-white">🚀 Publish to Marketplace</button>}
    </div>
  );
}
