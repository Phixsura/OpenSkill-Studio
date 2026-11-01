"use client";
export function FleetApiOpenapiV9Panel({ specs, errors }: { specs: number; errors: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📄 API OpenAPI v9</h3>
    <div className="text-sm">{specs} specs · {errors} lint errors</div>
  </div>);
}
