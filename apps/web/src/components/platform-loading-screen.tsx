"use client";

export function UplatformUloadingUscreen({ status = "operational" }: { status?: string }) {
  const colors: Record<string, string> = { operational: "text-green-600", degraded: "text-yellow-600", down: "text-red-600" };
  return <span className={`text-sm font-medium ${colors[status] || "text-gray-500"}`}>{status}</span>;
}
