import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageAnalyticsChart } from "@/components/usage-analytics-chart";

describe("UsageAnalyticsChart", () => {
  it("renders analytics", () => {
    const { container } = render(
      <UsageAnalyticsChart totalEvents={1000} uniqueUsers={250} avgPerDay={50}
        topAction="view" byAction={{ view: 600, click: 300, submit: 100 }} />
    );
    expect(container.textContent).toContain("Usage Analytics");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("250 users");
    expect(container.textContent).toContain("view");
    expect(container.textContent).toContain("click");
    expect(container.textContent).toContain("50");
  });
});
