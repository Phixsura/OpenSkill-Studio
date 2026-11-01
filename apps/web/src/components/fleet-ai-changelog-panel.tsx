"use client";
export function FleetAiChangelogPanel({ changelogs, active, releases, features, fixes, subscribers }: { changelogs: number; active: number; releases: number; features: number; fixes: number; subscribers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 AI Changelog</h3>
    <div className="text-sm">{active}/{changelogs} active · {releases} releases · {features} features · {fixes} fixes · {subscribers.toLocaleString()} subs</div>
  </div>);
}
