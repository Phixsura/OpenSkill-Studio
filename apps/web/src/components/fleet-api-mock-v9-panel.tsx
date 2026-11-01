"use client";
export function FleetApiMockV9Panel({ mocks, requests }: { mocks: number; requests: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎭 API Mock v9</h3>
    <div className="text-sm">{mocks} mocks · {requests.toLocaleString()} requests</div>
  </div>);
}
