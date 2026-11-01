"use client";
interface ReqFingerprintPanelProps { uniqueFingerprints: number; duplicateGroups: number;
  totalRequests: number; dedupSavingsPct: number; }
export function ReqFingerprintPanel({ uniqueFingerprints, duplicateGroups, totalRequests, dedupSavingsPct }: ReqFingerprintPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Request Fingerprints</h3>
        <span className="text-xs text-gray-400">{uniqueFingerprints} unique / {totalRequests} total · {dedupSavingsPct}% dedup</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Unique</span><div className="font-bold text-lg text-blue-500">{uniqueFingerprints}</div></div>
        <div><span className="text-gray-400">Duplicates</span><div className="font-bold text-lg text-yellow-600">{duplicateGroups}</div></div>
      </div>
    </div>
  );
}
