"use client";
export function FleetAiAbPanel({ experiments, active, users, winners }: { experiments: number; active: number; users: number; winners: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧪 AI A/B Testing</h3>
    <div className="text-sm">{active}/{experiments} active · {users.toLocaleString()} users · {winners} winners</div>
  </div>);
}
