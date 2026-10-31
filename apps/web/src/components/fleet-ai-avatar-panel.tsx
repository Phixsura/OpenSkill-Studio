"use client";
export function FleetAiAvatarPanel({ services, active, avatars, animations }: { services: number; active: number; avatars: number; animations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧑 AI Avatar</h3>
    <div className="text-sm">{active}/{services} active · {avatars.toLocaleString()} avatars · {animations.toLocaleString()} animations</div>
  </div>);
}
