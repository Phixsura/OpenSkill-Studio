"use client";
export function FleetApiErrorHandlerV9Panel({ handlers, errors }: { handlers: number; errors: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐛 Error Handler v9</h3>
    <div className="text-sm">{handlers} handlers · {errors} handled</div>
  </div>);
}
