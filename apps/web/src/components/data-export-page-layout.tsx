"use client";

interface ExportOption { id: string; label: string; description: string; icon: string; formats: string[]; estimated_size_kb: number; }
interface DataExportPageLayoutProps { exportOptions: ExportOption[]; onExport: (type: string, format: string) => void; }

export function DataExportPageLayout({ exportOptions, onExport }: DataExportPageLayoutProps) {
  const formatSize = (kb: number) => kb >= 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb} KB`;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Export Your Data</h1>
        <p className="mt-1 text-sm text-gray-500">Download a copy of your data in various formats.</p>
      </div>
      <div className="space-y-3">
        {exportOptions.map(opt => (
          <div key={opt.id} className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <span className="text-2xl">{opt.icon}</span>
                <div>
                  <h3 className="font-semibold">{opt.label}</h3>
                  <p className="text-sm text-gray-500">{opt.description}</p>
                  <p className="mt-1 text-xs text-gray-400">~{formatSize(opt.estimated_size_kb)}</p>
                </div>
              </div>
              <div className="flex gap-1">
                {opt.formats.map(f => (
                  <button key={f} onClick={() => onExport(opt.id, f)}
                    className="rounded border px-2 py-1 text-xs uppercase hover:bg-gray-50 dark:border-gray-600">
                    {f}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
