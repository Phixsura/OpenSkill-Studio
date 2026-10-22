"use client";

interface AppComparisonTableProps {
  appA: { name: string }; appB: { name: string };
  differences: Record<string, { a: unknown; b: unknown }>;
  installA: number; installB: number;
}

export function AppComparisonTable({ appA, appB, differences, installA, installB }: AppComparisonTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead><tr className="border-b"><th className="px-3 py-2">Field</th><th className="px-3 py-2">{appA.name}</th><th className="px-3 py-2">{appB.name}</th></tr></thead>
        <tbody>
          {Object.entries(differences).map(([field, { a, b }]) => (
            <tr key={field} className="border-b dark:border-gray-800">
              <td className="px-3 py-2 font-medium capitalize">{field}</td>
              <td className="px-3 py-2">{String(a)}</td>
              <td className="px-3 py-2">{String(b)}</td>
            </tr>
          ))}
          <tr className="border-b dark:border-gray-800">
            <td className="px-3 py-2 font-medium">Installs</td>
            <td className="px-3 py-2">{installA}</td><td className="px-3 py-2">{installB}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
