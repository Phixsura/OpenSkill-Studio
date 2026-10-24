"use client";

interface ControlResult { id: string; control: string; description: string; completed: boolean; }
interface ComplianceChecklistPanelProps { framework: string; results: ControlResult[];
  complianceDisplay: string; status: string; onToggle: (id: string) => void; }

export function ComplianceChecklistPanel({ framework, results, complianceDisplay, status, onToggle }: ComplianceChecklistPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">✅ {framework.toUpperCase()} Compliance</h3>
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold">{complianceDisplay}</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${
            status === "compliant" ? "bg-green-100 text-green-700" :
            status === "in_progress" ? "bg-yellow-100 text-yellow-700" :
            "bg-gray-100 text-gray-600"
          }`}>{status.replace("_", " ")}</span>
        </div>
      </div>
      <div className="space-y-2">
        {results.map(r => (
          <button key={r.id} onClick={() => onToggle(r.id)}
            className="flex items-center gap-3 w-full text-left px-3 py-2.5 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition">
            <span className={`w-5 h-5 rounded flex items-center justify-center text-xs border ${
              r.completed ? "bg-green-500 border-green-500 text-white" : "border-gray-300 dark:border-gray-600"
            }`}>{r.completed ? "✓" : ""}</span>
            <div>
              <p className="text-sm font-medium">{r.control}</p>
              <p className="text-xs text-gray-400">{r.description}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
