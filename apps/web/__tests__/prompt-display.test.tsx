import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { PromptDisplay } from "@/components/prompt-display";

describe("PromptDisplay", () => {
  it("renders structured prompt JSON", () => {
    const content = JSON.stringify({
      prompt: "Cinematic watch on marble",
      tool: "Seedream",
      model: "example-model",
      parameters: { aspect_ratio: "9:16" },
      notes: "key visual",
    });
    render(<PromptDisplay content={content} />);
    expect(screen.getByText("Cinematic watch on marble")).toBeDefined();
    expect(screen.getByText("Seedream")).toBeDefined();
    expect(screen.getByText("aspect_ratio")).toBeDefined();
    expect(screen.getByText("9:16")).toBeDefined();
    expect(screen.getByText(/key visual/)).toBeDefined();
  });

  it("falls back to raw text for non-JSON content", () => {
    render(<PromptDisplay content="just a plain prompt" />);
    expect(screen.getByText("just a plain prompt")).toBeDefined();
  });

  it("falls back to raw text for JSON without prompt key", () => {
    render(<PromptDisplay content='{"foo": "bar"}' />);
    expect(screen.getByText('{"foo": "bar"}')).toBeDefined();
  });

  it("renders nothing for null content", () => {
    const { container } = render(<PromptDisplay content={null} />);
    expect(container.innerHTML).toBe("");
  });

  it("omits parameters section when empty", () => {
    const content = JSON.stringify({ prompt: "p", parameters: {} });
    render(<PromptDisplay content={content} />);
    expect(screen.queryByText("Parameters")).toBeNull();
  });
});
