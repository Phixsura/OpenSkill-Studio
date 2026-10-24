"use client";

interface ErrorCode { code: string; message: string; status: number; category: string; }
interface ErrorCodeReferenceProps { codes: ErrorCode[]; categories: string[]; }

const STATUS_COLOR: Record<string, string> = {
  "400": "text-yellow-600", "401": "text-orange-600", "403": "text-red-500",
  "404": "text-gray-500", "409": "text-purple-500", "415": "text-gray-400",
  "429": "text-red-600", "500": "text-red-700", "503": "text-red-700",
};

export function ErrorCodeReference({ codes, categories }: ErrorCodeReferenceProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📖 Error Codes</h3>
        <p className="text-xs text-gray-400">{codes.length} codes · {categories.join(", ")}</p>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3 text-left">Code</th><th className="p-3">Status</th>
          <th className="p-3 text-left">Message</th><th className="p-3 text-left">Category</th>
        </tr></thead>
        <tbody>
          {codes.map(c => (
            <tr key={c.code} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-3 font-mono text-xs font-bold">{c.code}</td>
              <td className={`p-3 text-center font-bold ${STATUS_COLOR[String(c.status)] || ""}`}>{c.status}</td>
              <td className="p-3">{c.message}</td>
              <td className="p-3 text-xs text-gray-400 capitalize">{c.category}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
