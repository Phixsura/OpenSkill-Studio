import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIBillingEventCard from "../src/components/api-billing-event-card";

const byType = [
  { event_type: "api_call", amount: 15.0 },
  { event_type: "storage", amount: 3.0 },
];

describe("APIBillingEventCard", () => {
  it("renders total and count", () => {
    const { container } = render(<APIBillingEventCard byType={byType} total={18.0} currency="USD" eventCount={100} appName="App" />);
    expect(container.textContent).toContain("USD 18.00");
    expect(container.textContent).toContain("100 events");
  });

  it("shows type breakdown", () => {
    const { container } = render(<APIBillingEventCard byType={byType} total={18} currency="USD" eventCount={10} appName="App" />);
    expect(container.textContent).toContain("api_call");
    expect(container.textContent).toContain("USD 15.00");
  });

  it("shows empty state", () => {
    const { container } = render(<APIBillingEventCard byType={[]} total={0} currency="USD" eventCount={0} appName="App" />);
    expect(container.textContent).toContain("No billing events");
  });
});
