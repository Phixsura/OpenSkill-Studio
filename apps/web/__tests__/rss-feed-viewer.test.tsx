import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RssFeedViewer } from "@/components/rss-feed-viewer";

describe("RssFeedViewer", () => {
  it("renders feed", () => {
    const { container } = render(
      <RssFeedViewer title="OpenSkill Updates" itemCount={2} items={[
        { title: "v3.2 Released", link: "/v32", description: "New features", pubDate: "2026-10-24", category: "release" },
        { title: "New SDK", link: "/sdk", description: "TypeScript SDK", pubDate: "2026-10-23", category: "announcement" },
      ]} />
    );
    expect(container.textContent).toContain("OpenSkill Updates");
    expect(container.textContent).toContain("2 items");
    expect(container.textContent).toContain("v3.2 Released");
    expect(container.textContent).toContain("release");
    expect(container.textContent).toContain("New SDK");
  });
});
