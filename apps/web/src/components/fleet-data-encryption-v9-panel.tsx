"use client";
export function FleetDataEncryptionV9Panel({ resources, atRest }: { resources: number; atRest: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 Data Encryption v9</h3>
    <div className="text-sm">{resources} resources · {atRest} encrypted at rest</div>
  </div>);
}
