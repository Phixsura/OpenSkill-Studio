import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogRSSCard from "../src/components/changelog-rss-card";

const items = [
  { item_id: "i1", title: "v2.0 Release", version: "v2.0" },
  { item_id: "i2", title: "Bug fixes", version: "v1.1" },
];

describe("ChangelogRSSCard", () => {
  it("renders header and count", () => {
    const { container } = render(
      <ChangelogRSSCard
        feedTitle="My Changelog"
        feedLink="https://example.com/rss"
        items={items}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Changelog RSS");
    expect(container.textContent).toContain("2 items");
  });

  it("shows feed title and link", () => {
    const { container } = render(
      <ChangelogRSSCard
        feedTitle="My Changelog"
        feedLink="https://example.com/rss"
        items={items}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("My Changelog");
    expect(container.textContent).toContain("https://example.com/rss");
  });

  it("shows item titles and versions", () => {
    const { container } = render(
      <ChangelogRSSCard feedTitle="Log" feedLink="https://x" items={items} appName="App" />,
    );
    expect(container.textContent).toContain("v2.0 Release");
    expect(container.textContent).toContain("v1.1");
  });

  it("shows empty state", () => {
    const { container } = render(
      <ChangelogRSSCard feedTitle="Log" feedLink="https://x" items={[]} appName="App" />,
    );
    expect(container.textContent).toContain("No feed items");
  });
});
