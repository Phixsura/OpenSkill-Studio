"use client";
export function FleetAppwritePanel({ projects, active, databases, storageGb, functions }: { projects: number; active: number; databases: number; storageGb: number; functions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔴 Appwrite</h3>
    <div className="text-sm">{active}/{projects} active · {databases} DBs · {storageGb}GB · {functions} fns</div>
  </div>);
}
