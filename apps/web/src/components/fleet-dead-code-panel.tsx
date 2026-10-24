"use client";
export function FleetDeadCodePanel({ totalFiles, deadFiles, deadLoc, clean }: { totalFiles: number; deadFiles: number; deadLoc: number; clean: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💀 Dead Code</h3>
    {clean ? <span className="text-xs text-green-600">✅ No dead code</span>
     : <span className="text-xs text-yellow-600">⚠️ {deadFiles} dead files · {deadLoc.toLocaleString()} dead LOC</span>}
  </div>);
}
