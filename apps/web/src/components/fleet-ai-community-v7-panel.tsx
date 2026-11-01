"use client";
export function FleetAiCommunityV7Panel({ systems, active, members, contributors, discussions }: { systems: number; active: number; members: number; contributors: number; discussions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👥 AI Community v7</h3>
    <div className="text-sm">{active}/{systems} active · {members.toLocaleString()} members · {contributors.toLocaleString()} contributors · {discussions.toLocaleString()} discussions</div>
  </div>);
}
