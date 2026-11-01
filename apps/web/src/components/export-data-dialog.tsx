"use client";

interface ExportSection { section: string; label: string; included: boolean; estimatedSizeKb: number; }
interface ExportDataDialogProps { appName: string; sections: ExportSection[];
  estimatedSizeDisplay: string; onExport: (sections: string[]) => void; onCancel: () => void; }

export function ExportDataDialog({ appName, sections, estimatedSizeDisplay, onExport, onCancel }: ExportDataDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-xl border bg-white p-5 shadow-xl dark:bg-gray-900 dark:border-gray-700">
        <h2 className="text-lg font-bold">📤 Export {appName} Data</h2>
        <p className="mt-1 text-sm text-gray-500">Estimated size: {estimatedSizeDisplay}</p>
        <div className="mt-3 space-y-1">
          {sections.map(s => (
            <label key={s.section} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
              <div className="flex items-center gap-2">
                <input type="checkbox" defaultChecked={s.included} className="accent-blue-600" />
                <span className="text-sm">{s.label}</span>
              </div>
              <span className="text-xs text-gray-400">{s.estimatedSizeKb}KB</span>
            </label>
          ))}
        </div>
        <div className="mt-4 flex gap-3">
          <button onClick={onCancel} className="flex-1 rounded border py-2 text-sm dark:border-gray-700">Cancel</button>
          <button onClick={() => onExport(sections.filter(s => s.included).map(s => s.section))}
            className="flex-1 rounded bg-blue-600 py-2 text-sm text-white">Export JSON</button>
        </div>
      </div>
    </div>
  );
}
