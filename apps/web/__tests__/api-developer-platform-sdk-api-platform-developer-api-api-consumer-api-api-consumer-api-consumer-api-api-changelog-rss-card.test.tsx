import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-changelog-rss-card";

describe("ConsumerApiChangelogRssCard", () => {
  it("shows items", () => {
    const items = [{ id: "c1", title: "New Auth", version: "2.0", type: "feature", publishedAt: "2026-06-01" }];
    const { container } = render(<Card items={items} feedUrl="/api/changelog.rss" appName="App" />);
    expect(container.textContent).toContain("Changelog RSS");
    expect(container.textContent).toContain("New Auth");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("/api/changelog.rss");
  });
  it("shows empty", () => {
    const { container } = render(<Card items={[]} feedUrl="/rss" appName="App" />);
    expect(container.textContent).toContain("No changelog entries");
  });
});
