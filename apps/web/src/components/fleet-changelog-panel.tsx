"use client";
export function FleetChangelogPanel({ total, features, fixes, breaking }: { total: number; features: number; fixes: number; breaking: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 Changelog</h3>
    <div className="text-sm">✨ {features} features · 🐛 {fixes} fixes · 💔 {breaking} breaking</div>
  </div>);
}
