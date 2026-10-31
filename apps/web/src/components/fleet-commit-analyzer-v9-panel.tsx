"use client";
export function FleetCommitAnalyzerV9Panel({ total, conventional }: { total: number; conventional: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Commit Analyzer v9</h3>
    <div className="text-sm">{total} commits · {conventional} conventional</div>
  </div>);
}
