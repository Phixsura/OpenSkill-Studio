"use client";

interface PermissionMatrixProps {
  matrix: Record<string, Record<string, boolean>>;
  roles: string[]; actions: string[];
  onToggle: (role: string, action: string) => void;
}

export function PermissionMatrix({ matrix, roles, actions, onToggle }: PermissionMatrixProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b dark:border-gray-700">
            <th className="px-3 py-2 text-left font-medium">Action</th>
            {roles.map(r => <th key={r} className="px-3 py-2 text-center font-medium capitalize">{r}</th>)}
          </tr>
        </thead>
        <tbody>
          {actions.map(action => (
            <tr key={action} className="border-b dark:border-gray-800">
              <td className="px-3 py-2 font-mono text-xs">{action}</td>
              {roles.map(role => {
                const allowed = matrix[role]?.[action] ?? false;
                return (
                  <td key={role} className="px-3 py-2 text-center">
                    <button onClick={() => onToggle(role, action)}
                      className={`h-5 w-5 rounded border text-xs ${allowed ? "bg-green-500 border-green-500 text-white" : "dark:border-gray-600"}`}>
                      {allowed ? "✓" : ""}
                    </button>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
