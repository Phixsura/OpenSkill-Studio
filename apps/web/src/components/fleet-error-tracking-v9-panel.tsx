"use client";
export function FleetErrorTrackingV9Panel({ apps, errors }: { apps: number; errors: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐛 Error Tracking v9</h3>
    <div className="text-sm">{apps} apps · {errors} errors today</div>
  </div>);
}
