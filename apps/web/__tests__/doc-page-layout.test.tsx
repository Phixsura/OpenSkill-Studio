import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DocPageLayout } from "@/components/doc-page-layout";

describe("DocPageLayout", () => {
  it("renders doc with TOC", () => {
    const { container } = render(
      <DocPageLayout title="Getting Started" readTimeDisplay="3 min read" hasToc={true}
        headings={[
          { level: 1, text: "Introduction", slug: "introduction" },
          { level: 2, text: "Installation", slug: "installation" },
          { level: 2, text: "Configuration", slug: "configuration" },
        ]}>
        <p>Welcome to the docs</p>
      </DocPageLayout>
    );
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("3 min read");
    expect(container.textContent).toContain("On this page");
    expect(container.textContent).toContain("Introduction");
    expect(container.textContent).toContain("Installation");
    expect(container.textContent).toContain("Welcome to the docs");
  });
});
