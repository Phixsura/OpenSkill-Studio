"use client";

interface ConnResult { success: boolean; url: string; hostname: string;
  latencyMs?: number; tls?: boolean; error?: string; }
interface ConnectionTestPanelProps { results: ConnResult[]; passed: number;
  total: number; allPassed: boolean; onTest: () => void; }

export function ConnectionTestPanel({ results, passed, total, allPassed, onTest }: ConnectionTestPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🔌 Connection Tests</h3>
        <div className="flex gap-2">
          <span className={`text-xs px-2 py-0.5 rounded-full ${allPassed ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
            {passed}/{total} passed
          </span>
          <button onClick={onTest} className="text-xs px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Retest</button>
        </div>
      </div>
      <div className="space-y-2">
        {results.map(r => (
          <div key={r.url} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2 text-sm">
            <div className="flex items-center gap-2">
              <span>{r.success ? "✅" : "❌"}</span>
              <span className="font-mono text-xs">{r.hostname}</span>
              {r.tls && <span className="text-xs text-green-500">🔒</span>}
            </div>
            {r.success ? <span className="text-xs text-gray-400">{r.latencyMs}ms</span>
                       : <span className="text-xs text-red-500">{r.error}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
