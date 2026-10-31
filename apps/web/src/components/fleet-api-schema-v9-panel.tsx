"use client";
export function FleetApiSchemaV9Panel({ schemas, versions }: { schemas: number; versions: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📐 API Schema v9</h3>
    <div className="text-sm">{schemas} schemas · {versions} versions</div>
  </div>);
}
