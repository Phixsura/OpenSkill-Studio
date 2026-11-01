"use client";

import { useState } from "react";

interface ExportJob {
  id: string;
  dataTypes: string[];
  format: "json" | "csv";
  recordCount: number;
  createdAt: string;
}

interface ImportJob {
  id: string;
  status: "pending" | "validating" | "importing" | "completed" | "failed";
  totalRecords: number;
  imported: number;
  skipped: number;
  errors: string[];
}

const statusColors: Record<string, string> = {
  pending: "bg-gray-100 text-gray-600 dark:bg-gray-800",
  validating: "bg-blue-100 text-blue-600 dark:bg-blue-900/30",
  importing: "bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30",
  completed: "bg-green-100 text-green-700 dark:bg-green-900/30",
  failed: "bg-red-100 text-red-600 dark:bg-red-900/30",
};

export function DataPortabilityPanel({
  exports: exportJobs,
  imports: importJobs,
  availableTypes,
  onExport,
  onImport,
}: {
  exports: ExportJob[];
  imports: ImportJob[];
  availableTypes: string[];
  onExport?: (types: string[], format: string) => void;
  onImport?: (file: string) => void;
}) {
  const [tab, setTab] = useState<"export" | "import">("export");
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [format, setFormat] = useState("json");

  const toggleType = (t: string) => {
    setSelectedTypes((prev) =>
      prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]
    );
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📦 Data Portability</h2>

      <div className="flex gap-1">
        {(["export", "import"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`text-sm px-4 py-1.5 rounded-lg ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {t === "export" ? "Export" : "Import"}
          </button>
        ))}
      </div>

      {tab === "export" && (
        <div className="space-y-3">
          <div className="flex flex-wrap gap-1">
            {availableTypes.map((t) => (
              <button key={t} onClick={() => toggleType(t)}
                className={`text-xs px-2.5 py-1 rounded-full border ${
                  selectedTypes.includes(t) ? "bg-blue-600 text-white border-blue-600" : "border-gray-300 dark:border-gray-600"
                }`}>{t}</button>
            ))}
          </div>
          <button onClick={() => onExport?.(selectedTypes, format)}
            disabled={selectedTypes.length === 0}
            className="text-sm bg-green-600 text-white px-4 py-1.5 rounded-lg disabled:opacity-50">
            Export {selectedTypes.length} type{selectedTypes.length !== 1 ? "s" : ""}
          </button>

          {exportJobs.map((job) => (
            <div key={job.id} className="rounded-lg border dark:border-gray-700 p-3 text-sm">
              <div className="flex justify-between">
                <span>{job.dataTypes.join(", ")}</span>
                <span className="text-gray-400">{job.recordCount} records</span>
              </div>
              <span className="text-xs text-gray-400">{job.createdAt}</span>
            </div>
          ))}
        </div>
      )}

      {tab === "import" && (
        <div className="space-y-3">
          <button onClick={() => onImport?.("data.json")}
            className="text-sm bg-blue-600 text-white px-4 py-1.5 rounded-lg">
            Import File
          </button>

          {importJobs.map((job) => (
            <div key={job.id} className="rounded-lg border dark:border-gray-700 p-3">
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${statusColors[job.status]}`}>
                  {job.status}
                </span>
                <span className="text-sm">{job.imported}/{job.totalRecords} imported</span>
                {job.skipped > 0 && <span className="text-xs text-yellow-600">{job.skipped} skipped</span>}
              </div>
              {job.errors.length > 0 && (
                <div className="text-xs text-red-500">{job.errors[0]}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
