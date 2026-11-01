"use client";
interface RespTransformPanelProps { format: string; page: number; totalPages: number;
  total: number; perPage: number; hasNext: boolean; }
export function RespTransformPanel({ format, page, totalPages, total, perPage, hasNext }: RespTransformPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Response Transform</h3>
        <span className="text-xs text-gray-400">{format} · {total} items · {perPage}/page</span>
      </div>
      <div className="p-4 flex justify-between text-xs text-gray-400">
        <span>Page {page}/{totalPages}</span>
        <span>{hasNext ? "→ Next" : "Last page"}</span>
      </div>
    </div>
  );
}
