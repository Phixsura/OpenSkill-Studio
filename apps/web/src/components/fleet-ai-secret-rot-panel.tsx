"use client";
export function FleetAiSecretRotPanel({ rotators, active, secrets, rotations, avgAge }: { rotators: number; active: number; secrets: number; rotations: number; avgAge: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 AI Secret Rotation</h3>
    <div className="text-sm">{active}/{rotators} active · {secrets} secrets · {rotations} rotations · {avgAge}d avg age</div>
  </div>);
}
