import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiUsageSummaryCard from "../src/components/api-developer-api-api-developer-api-usage-summary-card";

const summaries = [
  { developer_id: "alice", total_requests: 50000, unique_endpoints: 20, error_rate_pct: 0.5, activity_level: "power" },
  { developer_id: "bob", total_requests: 500, unique_endpoints: 3, error_rate_pct: 2, activity_level: "moderate" },
];

describe("APIDeveloperAPIApiDeveloperApiUsageSummaryCard", () => {
  it("shows developer usage", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiUsageSummaryCard summaries={summaries} activityBreakdown={{ power: 1, moderate: 1 }} appName="App" />);
    expect(container.textContent).toContain("Developer Usage");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("50,000 reqs");
    expect(container.textContent).toContain("power");
    expect(container.textContent).toContain("moderate: 1");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiUsageSummaryCard summaries={[]} activityBreakdown={{}} appName="App" />);
    expect(container.textContent).toContain("No developer data");
  });
});
