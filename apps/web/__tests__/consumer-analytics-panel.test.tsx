import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConsumerAnalyticsPanel } from "@/components/consumer-analytics-panel";
describe("ConsumerAnalyticsPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ConsumerAnalyticsPanel totalConsumers={2} totalRequests={10000}
        consumers={[
          { consumerId: "app-1", requests: 7000, avgLatencyMs: 45, errorRatePct: 0.5 },
          { consumerId: "app-2", requests: 3000, avgLatencyMs: 120, errorRatePct: 5 },
        ]} />
    );
    expect(container.textContent).toContain("Consumer Analytics");
    expect(container.textContent).toContain("2 consumers");
    expect(container.textContent).toContain("10,000 reqs");
    expect(container.textContent).toContain("app-1");
    expect(container.textContent).toContain("7,000 reqs");
    expect(container.textContent).toContain("app-2");
  });
});
