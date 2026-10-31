"use client";
export function FleetAiPlatformTrustV7Panel({ systems, active, score, transparency, certs }: { systems: number; active: number; score: number; transparency: number; certs: string[]; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤝 AI Platform Trust v7</h3>
    <div className="text-sm">{active}/{systems} active · score {score} · {transparency}% transparent · {certs.join(", ")}</div>
  </div>);
}
