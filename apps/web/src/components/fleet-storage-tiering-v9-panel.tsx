"use client";
export function FleetStorageTieringV9Panel({ hot, warm, cold }: { hot: number; warm: number; cold: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗄️ Storage Tiering v9</h3>
    <div className="text-sm">🔴 {hot}GB hot · 🟡 {warm}GB warm · 🔵 {cold}GB cold</div>
  </div>);
}
