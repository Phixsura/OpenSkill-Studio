import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EmbedCodeGenerator } from "@/components/embed-code-generator";

describe("EmbedCodeGenerator", () => {
  it("renders embed code", () => {
    const { container } = render(
      <EmbedCodeGenerator iframe='<iframe src="https://x.com/embed/a"></iframe>'
        script='<script src="https://x.com/sdk.js"></script>'
        widgetUrl="https://x.com/embed/a" />
    );
    expect(container.textContent).toContain("Embed Code");
    expect(container.textContent).toContain("iframe");
    expect(container.textContent).toContain("script");
    expect(container.textContent).toContain("Copy");
    expect(container.textContent).toContain("Preview");
  });
});
