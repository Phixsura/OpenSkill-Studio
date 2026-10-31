"use client";
export function FleetBuildBuyPanel({ total, built, bought, oss, buildRatio }: { total: number; built: number; bought: number; oss: number; buildRatio: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏗️ Build vs Buy</h3>
    <div className="text-sm">🔨 {built} built · 💰 {bought} bought · 🌍 {oss} OSS ({buildRatio}% built)</div>
  </div>);
}
