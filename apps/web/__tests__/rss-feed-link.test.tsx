import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RssFeedLink } from "@/components/rss-feed-link";

describe("RssFeedLink", () => {
  it("renders feed link", () => {
    const { container } = render(
      <RssFeedLink feedUrl="/changelog/rss" atomUrl="/changelog/atom"
        appName="SuperApp" entryCount={15} />
    );
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("15 entries");
    expect(container.textContent).toContain("RSS");
    expect(container.textContent).toContain("Atom");
  });
});
