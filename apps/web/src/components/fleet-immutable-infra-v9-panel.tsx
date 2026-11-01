"use client";
export function FleetImmutableInfraV9Panel({ instances, immutable }: { instances: number; immutable: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧊 Immutable Infra v9</h3>
    <div className="text-sm">{instances} instances · {immutable} immutable</div>
  </div>);
}
