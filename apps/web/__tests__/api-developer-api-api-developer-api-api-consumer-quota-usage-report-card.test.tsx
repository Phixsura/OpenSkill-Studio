import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiConsumerQuotaUsageReportCard from "../src/components/api-developer-api-api-developer-api-api-consumer-quota-usage-report-card";

const entries = [
  { consumer_id: "acme", api_calls_used: 8000, api_calls_limit: 10000, api_usage_pct: 80, any_over_limit: false },
  { consumer_id: "beta", api_calls_used: 15000, api_calls_limit: 10000, api_usage_pct: 150, any_over_limit: true },
];

describe("APIDeveloperAPIApiDeveloperApiApiConsumerQuotaUsageReportCard", () => {
  it("shows quota report", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiConsumerQuotaUsageReportCard entries={entries} period="2025-01" overLimitCount={1} appName="App" />);
    expect(container.textContent).toContain("Quota Usage Report");
    expect(container.textContent).toContain("2025-01");
    expect(container.textContent).toContain("1 over limit");
    expect(container.textContent).toContain("8,000/10,000");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiConsumerQuotaUsageReportCard entries={[]} period="2025-01" overLimitCount={0} appName="App" />);
    expect(container.textContent).toContain("No quota data");
  });
});
