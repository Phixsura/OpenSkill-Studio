"use client";
export function FleetApiDocsPanel({ total, documented, withExamples, coveragePct }: { total: number; documented: number; withExamples: number; coveragePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📖 API Docs</h3>
    <div className={`text-lg font-bold ${coveragePct >= 90 ? "text-green-600" : "text-yellow-600"}`}>{coveragePct}%</div>
    <div className="text-xs text-gray-400">{documented}/{total} documented · {withExamples} with examples</div>
  </div>);
}
