"use client";
interface ErrorCode { code: string; message: string; httpStatus: number; category: string; }
export function ErrorCodeReference({ codes }: { codes: ErrorCode[] }) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📖 Error Codes</h2>
      <div className="space-y-0.5">{codes.map((c) => (
        <div key={c.code} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <code className="font-bold text-red-600">{c.code}</code>
            <span>{c.message}</span>
          </div>
          <div className="flex gap-2 text-xs text-gray-400">
            <span>{c.httpStatus}</span>
            <span className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{c.category}</span>
          </div>
        </div>
      ))}</div>
    </div>
  );
}
