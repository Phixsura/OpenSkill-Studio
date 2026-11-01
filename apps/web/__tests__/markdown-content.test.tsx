import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarkdownContent } from "@/components/markdown-content";

describe("MarkdownContent", () => {
  it("renders blocks", () => {
    const { container } = render(
      <MarkdownContent blocks={[
        { type: "heading", level: 1, text: "Hello World" },
        { type: "paragraph", text: "This is content." },
        { type: "code", language: "python", code: 'print("hi")' },
      ]} />
    );
    expect(container.textContent).toContain("Hello World");
    expect(container.textContent).toContain("This is content.");
    expect(container.textContent).toContain('print("hi")');
    expect(container.textContent).toContain("python");
  });
});
