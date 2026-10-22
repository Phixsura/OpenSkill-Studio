import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceFeedCard } from "@/components/marketplace-feed-card";

describe("MarketplaceFeedCard", () => {
  it("renders entries", () => {
    const entries = [{ title: "App v2.0", link: "/app", published: "2026-06-01", author: "Dev", summary: "Big update" }];
    const { container } = render(<MarketplaceFeedCard entries={entries} />);
    expect(container.textContent).toContain("App v2.0");
    expect(container.textContent).toContain("Big update");
  });
  it("empty state", () => {
    const { container } = render(<MarketplaceFeedCard entries={[]} />);
    expect(container.textContent).toContain("No recent updates");
  });
});
