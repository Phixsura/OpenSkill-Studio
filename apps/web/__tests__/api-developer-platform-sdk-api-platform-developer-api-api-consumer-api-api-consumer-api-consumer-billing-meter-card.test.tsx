import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-billing-meter-card";

describe("ConsumerBillingMeterCard", () => {
  it("shows meters", () => {
    const meters = [{ metric: "api_calls", total: 1500, count: 30 }, { metric: "data_transfer", total: 50000, count: 10 }];
    const { container } = render(<Card consumerId="c1" meters={meters} appName="App" />);
    expect(container.textContent).toContain("Billing Meter");
    expect(container.textContent).toContain("api_calls");
    expect(container.textContent).toContain("30 events");
  });
  it("shows empty", () => {
    const { container } = render(<Card consumerId="c1" meters={[]} appName="App" />);
    expect(container.textContent).toContain("No usage recorded");
  });
});
