"use client";
export function FleetAngularPanel({ apps, deployed, components, modules, avgBundle }: { apps: number; deployed: number; components: number; modules: number; avgBundle: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🅰️ Angular</h3>
    <div className="text-sm">{deployed}/{apps} deployed · {components} components · {modules} modules · {avgBundle}KB</div>
  </div>);
}
