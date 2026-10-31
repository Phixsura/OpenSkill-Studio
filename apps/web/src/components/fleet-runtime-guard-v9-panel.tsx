"use client";
export function FleetRuntimeGuardV9Panel({ guards, blocked }: { guards: number; blocked: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ Runtime Guard v9</h3>
    <div className="text-sm">{guards} guards · {blocked} blocked today</div>
  </div>);
}
