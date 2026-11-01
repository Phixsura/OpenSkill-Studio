"use client";
export function FleetPdbPanel({ total, violated, allCompliant }: { total: number; violated: number; allCompliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ Fleet PDB</h3>
    {allCompliant ? <span className="text-xs text-green-600">✅ All {total} PDBs compliant</span>
     : <span className="text-xs text-red-500">⚠️ {violated} PDB violations</span>}
  </div>);
}
