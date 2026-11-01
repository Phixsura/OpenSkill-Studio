"use client";
export function FleetD1Panel({ databases, active, rowsRead, rowsWritten }: { databases: number; active: number; rowsRead: number; rowsWritten: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ D1</h3>
    <div className="text-sm">{active}/{databases} active · {rowsRead.toLocaleString()} reads · {rowsWritten.toLocaleString()} writes</div>
  </div>);
}
