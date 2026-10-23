"use client";

interface MigrationStep { index: number; dataType: string; status: string;
  recordsMigrated: number; errors: number; }
interface MigrationWizardUiProps { source: string; destination: string;
  steps: MigrationStep[]; completed: number; total: number; status: string;
  onRunStep: (index: number) => void; }

const STATUS_ICON: Record<string, string> = {
  pending: "⬜", completed: "✅", completed_with_errors: "⚠️", running: "🔄",
};

export function MigrationWizardUi({ source, destination, steps, completed, total, status, onRunStep }: MigrationWizardUiProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700 max-w-lg">
      <h3 className="font-semibold mb-2">🔀 Data Migration</h3>
      <p className="text-xs text-gray-400 mb-4">{source} → {destination} · {completed}/{total} steps</p>
      <div className="space-y-2">
        {steps.map(s => (
          <div key={s.index} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2.5">
            <div className="flex items-center gap-2">
              <span>{STATUS_ICON[s.status] || "⬜"}</span>
              <span className="text-sm capitalize">{s.dataType}</span>
              {s.recordsMigrated > 0 && <span className="text-xs text-gray-400">{s.recordsMigrated.toLocaleString()} records</span>}
              {s.errors > 0 && <span className="text-xs text-red-500">{s.errors} errors</span>}
            </div>
            {s.status === "pending" && (
              <button onClick={() => onRunStep(s.index)}
                className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Migrate</button>
            )}
          </div>
        ))}
      </div>
      {status === "completed" && (
        <div className="mt-3 p-2 bg-green-50 dark:bg-green-900/20 rounded text-xs text-green-700 dark:text-green-400 text-center">
          ✅ Migration complete!
        </div>
      )}
    </div>
  );
}
