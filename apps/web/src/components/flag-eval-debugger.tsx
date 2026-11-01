"use client";

interface EvalResult { flag: string; enabled: boolean; matchedRule?: string; reason: string; }
interface FlagEvalDebuggerProps { results: EvalResult[]; userId: string; }

export function FlagEvalDebugger({ results, userId }: FlagEvalDebuggerProps) {
  const enabled = results.filter(r => r.enabled).length;
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏁 Flag Evaluation</h3>
        <span className="text-xs text-gray-400">user: {userId} · {enabled}/{results.length} on</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.flag} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${r.enabled ? "bg-green-500" : "bg-gray-400"}`} />
              <span className="text-sm font-mono">{r.flag}</span>
            </div>
            <div className="text-xs text-gray-400">
              {r.reason}{r.matchedRule ? `: ${r.matchedRule}` : ""}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
