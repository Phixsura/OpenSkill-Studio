"use client";

interface Section { type: string; order: number; }
interface LandingPageEditorProps { appName: string; sections: Section[]; availableTypes: string[];
  onAddSection: (type: string) => void; onRemoveSection: (index: number) => void; onPreview: () => void; }

export function LandingPageEditor({ appName, sections, availableTypes, onAddSection, onRemoveSection, onPreview }: LandingPageEditorProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{appName} Landing Page</h1>
        <div className="flex gap-2">
          <button onClick={onPreview} className="rounded border px-3 py-1.5 text-sm">Preview</button>
          <select onChange={e => { if (e.target.value) { onAddSection(e.target.value); e.target.value = ""; } }}
            defaultValue="" className="rounded border px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700">
            <option value="">+ Add Section</option>
            {availableTypes.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
      </div>
      <div className="space-y-2">
        {sections.map((s, i) => (
          <div key={i} className="flex items-center justify-between rounded-lg border border-gray-200 p-3 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">#{i + 1}</span>
              <span className="text-sm font-medium capitalize">{s.type}</span>
            </div>
            <button onClick={() => onRemoveSection(i)} className="text-xs text-red-500">Remove</button>
          </div>
        ))}
        {sections.length === 0 && (
          <p className="py-8 text-center text-sm text-gray-400">No sections yet. Add one above!</p>
        )}
      </div>
    </div>
  );
}
