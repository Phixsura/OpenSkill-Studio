"use client";
export function FleetAiRedTeamPanel({ teams, active, attacks, vulns, fixed }: { teams: number; active: number; attacks: number; vulns: number; fixed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔴 AI Red Teaming</h3>
    <div className="text-sm">{active}/{teams} active · {attacks.toLocaleString()} attacks · {vulns} vulns · {fixed} fixed</div>
  </div>);
}
