"use client";

interface RbacRoleComparisonProps { roleA: string; roleB: string;
  shared: string[]; onlyA: string[]; onlyB: string[]; }

export function RbacRoleComparison({ roleA, roleB, shared, onlyA, onlyB }: RbacRoleComparisonProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔐 Role Comparison</h3>
        <div className="text-xs text-gray-400 mt-0.5">{roleA} vs {roleB}</div>
      </div>
      <div className="grid grid-cols-3 divide-x dark:divide-gray-700">
        <div className="p-3">
          <div className="text-[10px] text-gray-400 mb-1">Only {roleA}</div>
          {onlyA.map(p => <div key={p} className="text-xs text-blue-600 font-mono py-0.5">+ {p}</div>)}
          {onlyA.length === 0 && <div className="text-[10px] text-gray-300">none</div>}
        </div>
        <div className="p-3">
          <div className="text-[10px] text-gray-400 mb-1">Shared ({shared.length})</div>
          {shared.map(p => <div key={p} className="text-xs text-gray-500 font-mono py-0.5">{p}</div>)}
        </div>
        <div className="p-3">
          <div className="text-[10px] text-gray-400 mb-1">Only {roleB}</div>
          {onlyB.map(p => <div key={p} className="text-xs text-green-600 font-mono py-0.5">+ {p}</div>)}
          {onlyB.length === 0 && <div className="text-[10px] text-gray-300">none</div>}
        </div>
      </div>
    </div>
  );
}
