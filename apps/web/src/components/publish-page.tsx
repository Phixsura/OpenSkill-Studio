"use client";

interface Step { id: string; label: string; auto: boolean; pass: boolean; icon: string; }
interface PublishPageProps { appName: string; version: string; releaseNotes: string;
  steps: Step[]; score: number; canPublish: boolean; cta: string;
  onPublish: () => void; onEditNotes: (notes: string) => void; }

export function PublishPage({ appName, version, releaseNotes, steps, score, canPublish,
  cta, onPublish, onEditNotes }: PublishPageProps) {
  return (
    <div className="mx-auto max-w-lg space-y-5">
      <h2 className="text-lg font-bold">📤 Publish {appName} v{version}</h2>
      <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full transition-all ${canPublish ? "bg-green-500" : "bg-blue-500"}`}
          style={{ width: `${score}%` }} />
      </div>
      <p className="text-xs text-center text-gray-400">{score}% ready</p>
      <div className="space-y-1">
        {steps.map(s => (
          <div key={s.id} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span>{s.icon}</span><span className="text-sm">{s.label}</span>
            </div>
            {s.auto && <span className="text-xs text-gray-400">auto</span>}
          </div>
        ))}
      </div>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Release Notes</label>
        <textarea value={releaseNotes} onChange={e => onEditNotes(e.target.value)} rows={3}
          className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
      </div>
      <button onClick={onPublish} disabled={!canPublish}
        className="w-full rounded-lg bg-green-600 py-3 text-sm font-medium text-white disabled:opacity-30">{cta}</button>
    </div>
  );
}
