"use client";
export function FleetFirebasePanel({ projects, active, authUsers, firestoreDocs, storageGb }: { projects: number; active: number; authUsers: number; firestoreDocs: number; storageGb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔥 Firebase</h3>
    <div className="text-sm">{active}/{projects} active · {authUsers.toLocaleString()} users · {firestoreDocs.toLocaleString()} docs</div>
  </div>);
}
