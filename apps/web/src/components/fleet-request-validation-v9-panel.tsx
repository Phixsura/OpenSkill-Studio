"use client";
export function FleetRequestValidationV9Panel({ validators, rejected }: { validators: number; rejected: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ Request Validation v9</h3>
    <div className="text-sm">{validators} validators · {rejected} rejected</div>
  </div>);
}
