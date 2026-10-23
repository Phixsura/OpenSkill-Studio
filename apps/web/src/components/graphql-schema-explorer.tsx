"use client";

interface SchemaField { name: string; type: string; required?: boolean; }
interface SchemaType { name: string; fields: SchemaField[]; }
interface GraphqlSchemaExplorerProps { types: SchemaType[]; queryCount: number; mutationCount: number; schema: string; }

export function GraphqlSchemaExplorer({ types, queryCount, mutationCount, schema }: GraphqlSchemaExplorerProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">GraphQL Schema</h2>
        <div className="flex gap-2 text-xs text-gray-400">
          <span>{types.length} types</span>
          <span>{queryCount} queries</span>
          <span>{mutationCount} mutations</span>
        </div>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {types.map(t => (
          <div key={t.name} className="rounded-lg border p-3 dark:border-gray-700">
            <p className="font-mono text-sm font-bold text-purple-600">{t.name}</p>
            <div className="mt-1.5 space-y-0.5">
              {t.fields.map(f => (
                <div key={f.name} className="flex justify-between font-mono text-xs">
                  <span>{f.name}</span>
                  <span className="text-blue-500">{f.type}{f.required ? "!" : ""}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      <details>
        <summary className="cursor-pointer text-sm text-gray-400">Raw Schema</summary>
        <pre className="mt-2 overflow-x-auto rounded bg-gray-900 p-3 font-mono text-xs text-green-400">{schema}</pre>
      </details>
    </div>
  );
}
