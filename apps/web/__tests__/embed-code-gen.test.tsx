import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EmbedCodeGen } from "@/components/embed-code-gen";

describe("EmbedCodeGen", () => {
  it("renders embed", () => {
    const { container } = render(
      <EmbedCodeGen appName="My App" iframeCode='<iframe src="test"></iframe>'
        embedUrl="https://test" onStyleChange={vi.fn()}
        styles={[{ id: "card", label: "Card", preview: "" }, { id: "badge", label: "Badge", preview: "" }]} />
    );
    expect(container.textContent).toContain("Embed Widget");
    expect(container.textContent).toContain("My App");
    expect(container.textContent).toContain("<iframe");
    expect(container.textContent).toContain("Card");
    expect(container.textContent).toContain("Badge");
    expect(container.textContent).toContain("Copy Embed Code");
  });
});
