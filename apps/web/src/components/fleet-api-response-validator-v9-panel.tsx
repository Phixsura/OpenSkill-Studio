"use client";
export function FleetApiResponseValidatorV9Panel({ validators, violations }: { validators: number; violations: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ Response Validator v9</h3>
    <div className="text-sm">{validators} validators · {violations} violations</div>
  </div>);
}
