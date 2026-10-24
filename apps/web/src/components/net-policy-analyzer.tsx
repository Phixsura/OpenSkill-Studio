"use client";

interface NetPolicyAnalyzerProps { total: number; allow: number; deny: number;
  overlyPermissive: string[]; securityScore: number; }

export function NetPolicyAnalyzer({ total, allow, deny, overlyPermissive, securityScore }: NetPolicyAnalyzerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔒 Network Policy Audit</h3>
        <span className="text-xs text-gray-400">{total} policies · score: {securityScore}/100</span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-2 text-center"><div className="text-sm font-bold text-green-600">{allow}</div><div className="text-[9px] text-gray-400">Allow</div></div>
        <div className="bg-white dark:bg-gray-900 p-2 text-center"><div className="text-sm font-bold text-red-500">{deny}</div><div className="text-[9px] text-gray-400">Deny</div></div>
        <div className="bg-white dark:bg-gray-900 p-2 text-center"><div className="text-sm font-bold text-yellow-600">{overlyPermissive.length}</div><div className="text-[9px] text-gray-400">Risky</div></div>
      </div>
      {overlyPermissive.length > 0 && (
        <div className="p-3 bg-yellow-50 dark:bg-yellow-900/10 text-xs text-yellow-700">
          ⚠ Overly permissive: {overlyPermissive.join(", ")}
        </div>
      )}
    </div>
  );
}
