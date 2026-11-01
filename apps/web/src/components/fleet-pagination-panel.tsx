"use client";
export function FleetPaginationPanel({ total, paginated, cursorBased, unpaginated }: { total: number; paginated: number; cursorBased: number; unpaginated: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📄 API Pagination</h3>
    <div className="text-sm">{paginated}/{total} paginated · {cursorBased} cursor-based</div>
    {unpaginated > 0 && <span className="text-xs text-yellow-600">⚠️ {unpaginated} unpaginated</span>}
  </div>);
}
