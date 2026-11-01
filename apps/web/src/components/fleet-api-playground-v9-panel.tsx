"use client";
export function FleetApiPlaygroundV9Panel({ playgrounds, users }: { playgrounds: number; users: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎮 API Playground v9</h3>
    <div className="text-sm">{playgrounds} playgrounds · {users} users</div>
  </div>);
}
