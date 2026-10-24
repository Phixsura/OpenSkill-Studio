"use client";
export function FleetResRecPanel({ total, overProv, underProv, rightSized, savingsPossible }: { total: number; overProv: number; underProv: number; rightSized: number; savingsPossible: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💡 Resource Recommendations</h3>
    <div className="text-sm">✅ {rightSized} right · ⬆️ {underProv} under · ⬇️ {overProv} over</div>
    {savingsPossible && <span className="text-xs text-green-600">💰 Cost savings possible</span>}
  </div>);
}
