"use client";
export function FleetA11yPanel({ total, wcagAa, wcagAaa, score, compliant }: { total: number; wcagAa: number; wcagAaa: number; score: number; compliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">♿ Accessibility</h3>
    <div className={`text-lg font-bold ${compliant ? "text-green-600" : "text-yellow-600"}`}>{score}% WCAG AA</div>
    <div className="text-xs text-gray-400">{wcagAa}/{total} AA · {wcagAaa} AAA</div>
  </div>);
}
