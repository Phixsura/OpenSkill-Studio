"use client";
export function FleetAiSchemaRegPanel({ registries, active, schemas, versions, validations }: { registries: number; active: number; schemas: number; versions: number; validations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📐 AI Schema Registry</h3>
    <div className="text-sm">{active}/{registries} active · {schemas} schemas · {versions} versions · {validations.toLocaleString()} validations</div>
  </div>);
}
