import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIChangelogWidgetAnalyticsCard from "../src/components/api-developer-api-changelog-widget-analytics-card";

const analytics = { total_impressions: 5000, total_clicks: 250, unique_viewers: 800, entries_read: 150, ctr: 5, read_rate: 60 };

describe("APIDeveloperAPIChangelogWidgetAnalyticsCard", () => {
  it("shows analytics", () => {
    const { container } = render(<APIDeveloperAPIChangelogWidgetAnalyticsCard analytics={analytics} appName="App" />);
    expect(container.textContent).toContain("Widget Analytics");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("5%");
    expect(container.textContent).toContain("60%");
  });
});
