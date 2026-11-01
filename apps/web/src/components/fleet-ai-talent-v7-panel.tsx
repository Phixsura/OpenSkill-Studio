"use client";
export function FleetAiTalentV7Panel({ systems, active, engineers, hiring, retention }: { systems: number; active: number; engineers: number; hiring: number; retention: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👥 AI Talent v7</h3>
    <div className="text-sm">{active}/{systems} active · {engineers} engineers · {hiring} hiring · {retention}% retention</div>
  </div>);
}
