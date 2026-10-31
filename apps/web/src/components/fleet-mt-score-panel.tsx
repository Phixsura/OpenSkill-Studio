"use client";
export function FleetMtScorePanel({ score, data, compute, network, enterpriseReady }: { score: number; data: number; compute: number; network: number; enterpriseReady: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏢 Multitenancy</h3>
    <div className={`text-lg font-bold ${enterpriseReady ? "text-green-600" : "text-yellow-600"}`}>{score}%</div>
    <div className="text-xs text-gray-400">Data {data} · Compute {compute} · Network {network}</div>
  </div>);
}
