import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperChangelogAnalyticsCard from "../src/components/api-developer-api-changelog-analytics-card";

const analytics = { total_views: 5000, unique_viewers: 800, total_reactions: 250, total_comments: 100, total_bookmarks: 150, engagement_rate: 10, most_viewed_version: "v3.0" };

describe("APIDeveloperChangelogAnalyticsCard", () => {
  it("shows analytics", () => {
    const { container } = render(<APIDeveloperChangelogAnalyticsCard analytics={analytics} appName="App" />);
    expect(container.textContent).toContain("Changelog Analytics");
    expect(container.textContent).toContain("10% engagement");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("v3.0");
  });
});
