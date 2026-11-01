"use client";
export function FleetAnsiblePanel({ total, ok, changed, failed }: { total: number; ok: number; changed: number; failed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 Ansible</h3>
    <div className="text-sm">{ok}✅ {changed}🔄 {failed}❌ of {total}</div>
  </div>);
}
