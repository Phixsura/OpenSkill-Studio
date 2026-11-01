import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogRssCard from "../src/components/api-developer-platform-sdk-consumer-api-changelog-rss-card";

describe("ChangelogRssCard", () => {
  it("renders title and entries", () => {
    const { container } = render(<ChangelogRssCard />);
    expect(container.textContent).toContain("Changelog RSS");
    expect(container.textContent).toContain("New Batch API");
    expect(container.textContent).toContain("Auth Fix");
  });

  it("shows categories and count", () => {
    const { container } = render(<ChangelogRssCard />);
    expect(container.textContent).toContain("feature");
    expect(container.textContent).toContain("breaking");
    expect(container.textContent).toContain("3 feed entries");
  });
});
