"use client";

import { useState } from "react";

export interface GenerationMeta {
  source?: string;
  prompt?: string;
  negative_prompt?: string;
  seed?: number;
  cfg_scale?: number;
  steps?: number;
  sampler?: string;
  size?: string;
  model?: string;
  model_hash?: string;
  clip_skip?: number;
  resources?: { type?: string; name?: string; weight?: number; version?: string }[];
  has_comfyui_workflow?: boolean;
}

/** Parse an item's content JSON and return the generation dict, if any. */
export function parseGenerationMeta(content: string | null): GenerationMeta | null {
  if (!content) return null;
  try {
    const parsed = JSON.parse(content);
    if (parsed && typeof parsed === "object" && parsed.generation) {
      return parsed.generation as GenerationMeta;
    }
  } catch {
    // not JSON — no metadata
  }
  return null;
}

/** Serialize back to A1111-style infotext (round-trip compatible copy). */
export function toInfotext(meta: GenerationMeta): string {
  const lines: string[] = [];
  if (meta.prompt) lines.push(meta.prompt);
  if (meta.negative_prompt) lines.push(`Negative prompt: ${meta.negative_prompt}`);
  const settings: string[] = [];
  if (meta.steps != null) settings.push(`Steps: ${meta.steps}`);
  if (meta.sampler) settings.push(`Sampler: ${meta.sampler}`);
  if (meta.cfg_scale != null) settings.push(`CFG scale: ${meta.cfg_scale}`);
  if (meta.seed != null) settings.push(`Seed: ${meta.seed}`);
  if (meta.size) settings.push(`Size: ${meta.size}`);
  if (meta.model_hash) settings.push(`Model hash: ${meta.model_hash}`);
  if (meta.model) settings.push(`Model: ${meta.model}`);
  if (meta.clip_skip != null) settings.push(`Clip skip: ${meta.clip_skip}`);
  if (settings.length) lines.push(settings.join(", "));
  return lines.join("\n");
}

function CollapsibleText({ text, label }: { text: string; label: string }) {
  const [open, setOpen] = useState(false);
  const long = text.length > 280;
  const shown = long && !open ? text.slice(0, 280) + "…" : text;
  return (
    <div>
      <p className="text-xs font-semibold uppercase text-[hsl(var(--muted-foreground))]">
        {label}
      </p>
      <pre className="mt-1 whitespace-pre-wrap rounded bg-[hsl(var(--secondary))] p-2 font-mono text-xs">
        {shown}
      </pre>
      {long && (
        <button
          type="button"
          onClick={() => setOpen(!open)}
          className="mt-0.5 text-xs text-[hsl(var(--primary))] hover:underline"
        >
          {open ? "Show less" : "Show more"}
        </button>
      )}
    </div>
  );
}

/**
 * Generation-data panel (Civitai-style): renders the parameters extracted
 * from an AI-generated file, with one-click copy of the full infotext.
 */
export function GenerationData({ meta }: { meta: GenerationMeta }) {
  const [copied, setCopied] = useState(false);

  const params: [string, string][] = [];
  if (meta.sampler) params.push(["Sampler", meta.sampler]);
  if (meta.cfg_scale != null) params.push(["CFG", String(meta.cfg_scale)]);
  if (meta.steps != null) params.push(["Steps", String(meta.steps)]);
  if (meta.seed != null) params.push(["Seed", String(meta.seed)]);
  if (meta.size) params.push(["Size", meta.size]);
  if (meta.clip_skip != null) params.push(["Clip skip", String(meta.clip_skip)]);
  if (meta.model)
    params.push([
      "Model",
      meta.model + (meta.model_hash ? ` (${meta.model_hash.slice(0, 10)})` : ""),
    ]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(toInfotext(meta));
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard unavailable — ignore
    }
  };

  return (
    <div className="space-y-2 rounded-md border p-3">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold uppercase text-[hsl(var(--muted-foreground))]">
          Generation data
          <span className="ml-2 font-normal normal-case">
            (extracted from file{meta.source ? ` · ${meta.source}` : ""})
          </span>
        </p>
        <button
          type="button"
          onClick={handleCopy}
          className="rounded border px-2 py-0.5 text-xs hover:bg-[hsl(var(--secondary))]"
        >
          {copied ? "Copied ✓" : "Copy all"}
        </button>
      </div>

      {meta.prompt && <CollapsibleText text={meta.prompt} label="Prompt" />}
      {meta.negative_prompt && (
        <CollapsibleText text={meta.negative_prompt} label="Negative prompt" />
      )}

      {params.length > 0 && (
        <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs sm:grid-cols-3">
          {params.map(([k, v]) => (
            <div key={k}>
              <span className="text-[hsl(var(--muted-foreground))]">{k}:</span>{" "}
              <span className="font-mono">{v}</span>
            </div>
          ))}
        </div>
      )}

      {meta.resources && meta.resources.length > 0 && (
        <div>
          <p className="text-xs font-semibold uppercase text-[hsl(var(--muted-foreground))]">
            Resources
          </p>
          <ul className="mt-1 space-y-0.5 text-xs">
            {meta.resources.map((r, i) => (
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

      {meta.has_comfyui_workflow && (
        <p className="text-xs text-[hsl(var(--muted-foreground))]">
          🧩 This file contains an embedded ComfyUI workflow — download the original PNG and drag
          it onto a ComfyUI canvas to restore it.
        </p>
      )}
    </div>
  );
}
