"use client";
export function FleetAiPlatChlogV2Panel({ logs, active, releases, features, fixes, subscribers }: { logs: number; active: number; releases: number; features: number; fixes: number; subscribers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 AI Changelog v2</h3>
    <div className="text-sm">{active}/{logs} active · {releases} releases · {features} features · {fixes} fixes · {subscribers.toLocaleString()} subs</div>
  </div>);
}
