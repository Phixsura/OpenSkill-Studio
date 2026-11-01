import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIQuickStatsCard from "../src/components/api-developer-api-quick-stats-card";

const stats = { requests_today: 50000, errors_today: 100, active_developers: 25, webhook_deliveries_today: 10000, avg_response_ms: 45, uptime_today: 99.99 };

describe("APIDeveloperAPIQuickStatsCard", () => {
  it("shows today stats", () => {
    const { container } = render(<APIDeveloperAPIQuickStatsCard stats={stats} appName="App" />);
    expect(container.textContent).toContain("Quick Stats");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("99.99%");
  });
});
