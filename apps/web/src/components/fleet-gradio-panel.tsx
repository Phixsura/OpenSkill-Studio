"use client";
export function FleetGradioPanel({ apps, running, interfaces, users }: { apps: number; running: number; interfaces: number; users: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎨 Gradio</h3>
    <div className="text-sm">{running}/{apps} running · {interfaces} interfaces · {users.toLocaleString()} users</div>
  </div>);
}
