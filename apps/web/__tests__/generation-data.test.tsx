import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import {
  GenerationData,
  parseGenerationMeta,
  toInfotext,
  type GenerationMeta,
} from "@/components/generation-data";

const META: GenerationMeta = {
  source: "a1111",
  prompt: "cinematic watch on marble",
  negative_prompt: "blurry, low quality",
  seed: 2049363429,
  cfg_scale: 4.5,
  steps: 30,
  sampler: "Euler a",
  size: "832x1216",
  model: "WAI-illustrious",
  model_hash: "748cm123ab",
};

describe("parseGenerationMeta", () => {
  it("parses generation dict from item content", () => {
    const content = JSON.stringify({ generation: META });
    const parsed = parseGenerationMeta(content);
    expect(parsed?.seed).toBe(2049363429);
  });

  it("returns null for null content", () => {
    expect(parseGenerationMeta(null)).toBeNull();
  });

  it("returns null for non-JSON", () => {
    expect(parseGenerationMeta("plain text")).toBeNull();
  });

  it("returns null for JSON without generation key", () => {
    expect(parseGenerationMeta('{"prompt": "x"}')).toBeNull();
  });
});

describe("toInfotext", () => {
  it("serializes round-trip compatible A1111 infotext", () => {
    const text = toInfotext(META);
    expect(text).toContain("cinematic watch on marble");
    expect(text).toContain("Negative prompt: blurry, low quality");
    expect(text).toContain("Steps: 30");
    expect(text).toContain("Seed: 2049363429");
    expect(text).toContain("CFG scale: 4.5");
    expect(text).toContain("Model: WAI-illustrious");
  });

  it("omits absent fields", () => {
    const text = toInfotext({ prompt: "just a prompt" });
    expect(text).toBe("just a prompt");
  });
});

describe("GenerationData", () => {
  it("renders prompt, negative, and params grid", () => {
    render(<GenerationData meta={META} />);
    expect(screen.getByText("cinematic watch on marble")).toBeDefined();
    expect(screen.getByText("blurry, low quality")).toBeDefined();
    expect(screen.getByText("2049363429")).toBeDefined();
    expect(screen.getByText("Euler a")).toBeDefined();
    expect(screen.getByText("Copy all")).toBeDefined();
  });

  it("renders resources with weights", () => {
    render(
      <GenerationData
        meta={{ prompt: "p", resources: [{ type: "lora", name: "style-x", weight: 0.8 }] }}
      />,
    );
    expect(screen.getByText("style-x")).toBeDefined();
    expect(screen.getByText("×0.8")).toBeDefined();
  });

  it("shows ComfyUI workflow hint", () => {
    render(<GenerationData meta={{ prompt: "p", has_comfyui_workflow: true }} />);
    expect(screen.getByText(/ComfyUI workflow/)).toBeDefined();
  });

  it("collapses long prompts with Show more", () => {
    render(<GenerationData meta={{ prompt: "x".repeat(500), steps: 10 }} />);
    expect(screen.getByText("Show more")).toBeDefined();
  });
});
