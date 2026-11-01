"use client";
export function FleetStatusPageV9Panel({ components, operational }: { components: number; operational: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🟢 Status Page v9</h3>
    <div className="text-sm">{components} components · {operational} operational</div>
  </div>);
}
