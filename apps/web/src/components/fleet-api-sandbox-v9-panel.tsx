"use client";
export function FleetApiSandboxV9Panel({ sandboxes, users }: { sandboxes: number; users: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏖️ API Sandbox v9</h3>
    <div className="text-sm">{sandboxes} sandboxes · {users} users</div>
  </div>);
}
