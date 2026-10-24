"use client";
export function FleetStreamlitPanel({ apps, deployed, viewers, components }: { apps: number; deployed: number; viewers: number; components: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Streamlit</h3>
    <div className="text-sm">{deployed}/{apps} deployed · {viewers.toLocaleString()} viewers · {components} components</div>
  </div>);
}
