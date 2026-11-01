"use client";
export function FleetAiAccessGovV7Panel({ systems, active, users, roles, reviews, excessive }: { systems: number; active: number; users: number; roles: number; reviews: number; excessive: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 AI Access Gov v7</h3>
    <div className="text-sm">{active}/{systems} active · {users.toLocaleString()} users · {roles} roles · {reviews} reviews · {excessive} excessive</div>
  </div>);
}
