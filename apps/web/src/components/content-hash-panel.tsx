"use client";

interface HashResult { name: string; match: boolean; }
interface ContentHashPanelProps { results: HashResult[]; passed: number; failed: number; allValid: boolean; }

export function ContentHashPanel({ results, passed, failed, allValid }: ContentHashPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">#️⃣ Content Integrity</h3>
        <span className={`text-xs font-bold ${allValid ? "text-green-600" : "text-red-500"}`}>
          {allValid ? "✅ All valid" : `❌ ${failed} failed`} · {passed + failed} checked
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{r.name}</span>
            <span className={r.match ? "text-green-600" : "text-red-500"}>{r.match ? "✅" : "❌"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
