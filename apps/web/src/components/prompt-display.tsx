"use client";

interface PromptData {
  prompt?: string;
  tool?: string | null;
  model?: string | null;
  parameters?: Record<string, unknown> | null;
  notes?: string | null;
}

/**
 * Renders a prompt submission (stored as JSON in item content) as a
 * structured card. Falls back to raw text if the content isn't valid JSON.
 */
export function PromptDisplay({ content }: { content: string | null }) {
  if (!content) return null;

  let data: PromptData | null = null;
  try {
    const parsed = JSON.parse(content);
    if (parsed && typeof parsed === "object" && typeof parsed.prompt === "string") {
      data = parsed;
    }
  } catch {
    // Not JSON — render as plain text below
  }

  if (!data) {
    return <pre className="whitespace-pre-wrap rounded-md border p-3 text-sm">{content}</pre>;
  }

  const params = data.parameters && Object.keys(data.parameters).length > 0 ? data.parameters : null;

  return (
    <div className="space-y-3 rounded-md border p-4">
      <div>
        <p className="text-xs font-semibold uppercase text-[hsl(var(--muted-foreground))]">
          Prompt
        </p>
        <pre className="mt-1 whitespace-pre-wrap rounded bg-[hsl(var(--secondary))] p-3 font-mono text-sm">
          {data.prompt}
        </pre>
      </div>

      {(data.tool || data.model) && (
        <div className="flex flex-wrap gap-4 text-sm">
          {data.tool && (
            <span>
              <span className="text-[hsl(var(--muted-foreground))]">Tool:</span> {data.tool}
            </span>
          )}
          {data.model && (
            <span>
              <span className="text-[hsl(var(--muted-foreground))]">Model:</span> {data.model}
            </span>
          )}
        </div>
      )}

      {params && (
        <div>
          <p className="text-xs font-semibold uppercase text-[hsl(var(--muted-foreground))]">
            Parameters
          </p>
          <table className="mt-1 text-sm">
            <tbody>
              {Object.entries(params).map(([k, v]) => (
                <tr key={k}>
                  <td className="pr-4 text-[hsl(var(--muted-foreground))]">{k}</td>
                  <td className="font-mono">{typeof v === "string" ? v : JSON.stringify(v)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data.notes && (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">📝 {data.notes}</p>
      )}
    </div>
  );
}
