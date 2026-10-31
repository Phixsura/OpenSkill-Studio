"use client";
export function FleetThreatIntelV9Panel({ feeds, blocked }: { feeds: number; blocked: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 Threat Intel v9</h3>
    <div className="text-sm">{feeds} feeds · {blocked} blocked today</div>
  </div>);
}
