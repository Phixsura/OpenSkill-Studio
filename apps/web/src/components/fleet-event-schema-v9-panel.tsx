"use client";
export function FleetEventSchemaV9Panel({ schemas, compatible }: { schemas: number; compatible: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Event Schema v9</h3>
    <div className="text-sm">{schemas} schemas · {compatible} compatible</div>
  </div>);
}
