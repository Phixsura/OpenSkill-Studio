import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIChangelogSummaryCard from "../src/components/api-developer-api-changelog-summary-card";

const summary = { total_versions: 25, total_entries: 150, breaking_changes: 5, total_subscribers: 200, total_reactions: 1500, total_comments: 300 };

describe("APIDeveloperAPIChangelogSummaryCard", () => {
  it("shows all stats", () => {
    const { container } = render(<APIDeveloperAPIChangelogSummaryCard summary={summary} appName="App" />);
    expect(container.textContent).toContain("Changelog Summary");
    expect(container.textContent).toContain("25");
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("1500");
  });
});
