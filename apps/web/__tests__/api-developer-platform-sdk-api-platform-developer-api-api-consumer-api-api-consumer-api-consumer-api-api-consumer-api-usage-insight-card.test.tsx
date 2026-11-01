import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-usage-insight-card";

describe("ConsumerApiUsageInsightCard", () => {
  it("shows insights", () => {
    const insights = [{ id: "i1", category: "performance", severity: "critical", title: "High Error Rate", description: "8% errors", recommendation: "Check logs" }];
    const { container } = render(<Card insights={insights} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Usage Insights");
    expect(container.textContent).toContain("High Error Rate");
    expect(container.textContent).toContain("Check logs");
  });
  it("shows all good", () => {
    const { container } = render(<Card insights={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("All good");
  });
});
