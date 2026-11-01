"use client";

interface CspConfigEditorProps {
  allowEval: boolean; allowInline: boolean; origins: string[];
  onToggleEval: (v: boolean) => void; onToggleInline: (v: boolean) => void;
}

export function CspConfigEditor({ allowEval, allowInline, origins, onToggleEval, onToggleInline }: CspConfigEditorProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Content Security Policy</h3>
      <div className="mt-3 space-y-2">
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={allowEval} onChange={e => onToggleEval(e.target.checked)} />
          Allow unsafe-eval <span className="text-xs text-red-500">(security risk)</span>
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={allowInline} onChange={e => onToggleInline(e.target.checked)} />
          Allow unsafe-inline
        </label>
      </div>
      {origins.length > 0 && (
        <div className="mt-3">
          <p className="text-xs font-medium text-gray-500">Allowed Origins</p>
          <ul className="mt-1 space-y-1">
            {origins.map(o => <li key={o} className="text-xs font-mono text-gray-600 dark:text-gray-400">{o}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
