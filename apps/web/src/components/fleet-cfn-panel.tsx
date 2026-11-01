"use client";
export function FleetCfnPanel({ total, complete, rollback, inProgress }: { total: number; complete: number; rollback: number; inProgress: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 CloudFormation</h3>
    <div className="text-sm">{complete}✅ {rollback}⏪ {inProgress}🔄 of {total}</div>
  </div>);
}
