"use client";
export function FleetInfraHealthV9Panel({ components, score }: { components: number; score: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💚 Infra Health v9</h3>
    <div className="text-sm">{components} components · {score}/100</div>
  </div>);
}
