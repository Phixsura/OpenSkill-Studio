"use client";
export function FleetApiFieldValidationV9Panel({ rules, fields }: { rules: number; fields: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ Field Validation v9</h3>
    <div className="text-sm">{rules} rules · {fields.toLocaleString()} fields</div>
  </div>);
}
