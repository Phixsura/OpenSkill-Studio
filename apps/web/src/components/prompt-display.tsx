"use client";

import { useState } from "react";

import { toInfotext, type GenerationMeta } from "@/components/generation-data";

interface PromptData {
  prompt?: string;
  negative_prompt?: string | null;
  tool?: string | null;
  model?: string | null;
  seed?: number | null;
  cfg_scale?: number | null;
  steps?: number | null;
  sampler?: string | null;
  resources?: { type?: string; name?: string; weight?: number; version?: string }[] | null;
  parameters?: Record<string, unknown> | null;
  notes?: string | null;
}

/**
 * Renders a prompt submission (stored as JSON in item content) as a
 * structured card. Falls back to raw text if the content isn't valid JSON.
 */
export function PromptDisplay({ content }: { content: string | null }) {
  const [copied, setCopied] = useState(false);
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

  const chips: [string, string][] = [];
  if (data.seed != null) chips.push(["Seed", String(data.seed)]);
  if (data.cfg_scale != null) chips.push(["CFG", String(data.cfg_scale)]);
  if (data.steps != null) chips.push(["Steps", String(data.steps)]);
  if (data.sampler) chips.push(["Sampler", data.sampler]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(toInfotext(data as GenerationMeta));
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard unavailable
    }
  };

  return (
    <div className="space-y-3 rounded-md border p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-semibold uppercase text-[hsl(var(--muted-foreground))]">
            Prompt
          </p>
          <pre className="mt-1 whitespace-pre-wrap rounded bg-[hsl(var(--secondary))] p-3 font-mono text-sm">
            {data.prompt}
          </pre>
        </div>
        <button
          type="button"
          onClick={handleCopy}
          className="shrink-0 rounded border px-2 py-0.5 text-xs hover:bg-[hsl(var(--secondary))]"
        >
          {copied ? "Copied ✓" : "Copy all"}
        </button>
      </div>

      {data.negative_prompt && (
        <div>
          <p className="text-xs font-semibold uppercase text-[hsl(var(--muted-foreground))]">
            Negative prompt
          </p>
          <pre className="mt-1 whitespace-pre-wrap rounded bg-[hsl(var(--secondary))] p-3 font-mono text-sm">
            {data.negative_prompt}
          </pre>
        </div>
      )}

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

      {chips.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {chips.map(([k, v]) => (
            <span
              key={k}
              className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs"
            >
              <span className="text-[hsl(var(--muted-foreground))]">{k}</span>{" "}
              <span className="font-mono">{v}</span>
            </span>
          ))}
        </div>
      )}

      {data.resources && data.resources.length > 0 && (
        <div>
          <p className="text-xs font-semibold uppercase text-[hsl(var(--muted-foreground))]">
            Resources
          </p>
          <ul className="mt-1 space-y-0.5 text-xs">
            {data.resources.map((r, i) => (
              <li key={i} className="flex items-center gap-2">
                <span className="rounded-full bg-[hsl(var(--secondary))] px-1.5 py-0.5 uppercase">
                  {r.type ?? "resource"}
                </span>
                <span>{r.name}</span>
                {r.weight != null && (
                  <span className="font-mono text-[hsl(var(--muted-foreground))]">
                    ×{r.weight}
                  </span>
                )}
                {r.version && (
                  <span className="text-[hsl(var(--muted-foreground))]">{r.version}</span>
                )}
              </li>
            ))}
          </ul>
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
