import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-billing-summary-card";

describe("ConsumerBillingSummaryCard", () => {
  it("shows summaries", () => {
    const summaries = [{ consumer_id: "c1", period: "2024-01", total_dollars: "$62.99", tier: "pro", total_requests: 50000 }];
    const { container } = render(<Card summaries={summaries} totalRevenue="$62.99" appName="App" />);
    expect(container.textContent).toContain("Billing Summary");
    expect(container.textContent).toContain("$62.99");
    expect(container.textContent).toContain("pro");
  });
  it("shows empty", () => {
    const { container } = render(<Card summaries={[]} totalRevenue="$0.00" appName="App" />);
    expect(container.textContent).toContain("No billing data");
  });
});
