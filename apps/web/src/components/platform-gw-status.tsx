"use client";

interface Route { path: string; service: string; methods: string[]; }
interface PlatformGwStatusProps { routes: Route[]; middleware: string[];
  totalRequests: number; status: string; }

export function PlatformGwStatus({ routes, middleware, totalRequests, status }: PlatformGwStatusProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌐 Platform Gateway</h3>
        <span className={`text-xs font-bold ${status === "healthy" ? "text-green-600" : "text-red-500"}`}>
          {status} · {totalRequests.toLocaleString()} reqs
        </span>
      </div>
      <div className="p-3 text-xs text-gray-400">
        Middleware: {middleware.join(" → ")}
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {routes.map(r => (
          <div key={r.path} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{r.path}</span>
            <div className="flex items-center gap-2">
              <span className="text-blue-500">{r.service}</span>
              <span className="text-gray-400">{r.methods.join(", ")}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
