"use client";
export function FleetGitlabCiPanel({ total, success, failed, avgDuration }: { total: number; success: number; failed: number; avgDuration: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🦊 GitLab CI</h3>
    <div className="text-sm">{success}✅ {failed}❌ · avg {avgDuration}min</div>
  </div>);
}
