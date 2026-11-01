"use client";
export function FleetChefPanel({ profiles, passed, failed, skipped, compliancePct }: { profiles: number; passed: number; failed: number; skipped: number; compliancePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👨‍🍳 Chef InSpec</h3>
    <div className="text-sm">{compliancePct}% compliant · {passed}✅ {failed}❌ {skipped}⏭️</div>
  </div>);
}
