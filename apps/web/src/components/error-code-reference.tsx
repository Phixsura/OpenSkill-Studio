"use client";

interface ErrorCode { code: string; status: number; message: string; }

interface ErrorCodeReferenceProps { errors: ErrorCode[]; }

export function ErrorCodeReference({ errors }: ErrorCodeReferenceProps) {
  if (errors.length === 0) return null;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead><tr className="border-b dark:border-gray-700">
          <th className="px-3 py-2 font-medium">Code</th>
          <th className="px-3 py-2 font-medium">Status</th>
          <th className="px-3 py-2 font-medium">Message</th>
        </tr></thead>
        <tbody>
          {errors.map(e => (
            <tr key={e.code} className="border-b dark:border-gray-800">
              <td className="px-3 py-2 font-mono text-xs">{e.code}</td>
              <td className="px-3 py-2"><span className={`rounded px-1.5 py-0.5 text-xs ${e.status < 500 ? "bg-yellow-100" : "bg-red-100"}`}>{e.status}</span></td>
              <td className="px-3 py-2 text-gray-600 dark:text-gray-400">{e.message}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
