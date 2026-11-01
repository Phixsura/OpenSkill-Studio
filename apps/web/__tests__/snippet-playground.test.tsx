import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SnippetPlayground } from "@/components/snippet-playground";

describe("SnippetPlayground", () => {
  it("renders playground", () => {
    const { container } = render(
      <SnippetPlayground languages={["python", "javascript"]} currentLanguage="python"
        output="Hello, World!" running={false} onRun={vi.fn()} onLanguageChange={vi.fn()} />
    );
    expect(container.textContent).toContain("Playground");
    expect(container.textContent).toContain("Run");
    expect(container.textContent).toContain("Hello, World!");
  });
});
