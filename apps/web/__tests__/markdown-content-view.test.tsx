import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarkdownContentView } from "@/components/markdown-content-view";

describe("MarkdownContentView", () => {
  const headings = [
    { level: 1, text: "Intro", id: "intro" },
    { level: 2, text: "Setup", id: "setup" },
  ];
  it("renders with toc", () => {
    const { container } = render(
      <MarkdownContentView htmlContent="<h1>Intro</h1><p>Hello</p>" headings={headings} showToc={true} />
    );
    expect(container.textContent).toContain("Contents");
    expect(container.textContent).toContain("Intro");
    expect(container.textContent).toContain("Setup");
    expect(container.textContent).toContain("Hello");
  });
  it("renders without toc", () => {
    const { container } = render(
      <MarkdownContentView htmlContent="<p>Content</p>" headings={[]} showToc={false} />
    );
    expect(container.textContent).toContain("Content");
    expect(container.textContent).not.toContain("Contents");
  });
});
