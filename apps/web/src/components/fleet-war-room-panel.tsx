"use client";
export function FleetWarRoomPanel({ total, active, resolved, avgDuration, calm }: { total: number; active: number; resolved: number; avgDuration: number; calm: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 War Rooms</h3>
    {calm ? <span className="text-xs text-green-600">✅ No active war rooms</span>
     : <span className="text-xs text-red-500">🔴 {active} active · avg {avgDuration}min</span>}
  </div>);
}
