"use client";

interface SchemaAnalysis { totalTypes: number; byKind: Record<string, number>;
  totalFields: number; queries: string[]; mutations: string[]; complexity: string; }
interface GraphqlSchemaExplorerProps { analysis: SchemaAnalysis; }

export function GraphqlSchemaExplorer({ analysis }: GraphqlSchemaExplorerProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🔮 GraphQL Schema</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          analysis.complexity === "high" ? "bg-red-100 text-red-700" :
          analysis.complexity === "medium" ? "bg-yellow-100 text-yellow-700" :
          "bg-green-100 text-green-700"
        }`}>{analysis.complexity} complexity</span>
      </div>
      <div className="grid grid-cols-3 gap-3 mb-4 text-center">
        <div><p className="text-lg font-bold">{analysis.totalTypes}</p><p className="text-xs text-gray-400">Types</p></div>
        <div><p className="text-lg font-bold">{analysis.totalFields}</p><p className="text-xs text-gray-400">Fields</p></div>
        <div><p className="text-lg font-bold">{analysis.queries.length + analysis.mutations.length}</p><p className="text-xs text-gray-400">Operations</p></div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Queries ({analysis.queries.length})</h4>
          {analysis.queries.map(q => (
            <p key={q} className="text-sm font-mono text-blue-600 dark:text-blue-400">{q}</p>
          ))}
        </div>
        <div>
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Mutations ({analysis.mutations.length})</h4>
          {analysis.mutations.map(m => (
            <p key={m} className="text-sm font-mono text-purple-600 dark:text-purple-400">{m}</p>
          ))}
        </div>
      </div>
    </div>
  );
}
