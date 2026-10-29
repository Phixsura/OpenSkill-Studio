import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIConsumerQuotaCard from "../src/components/api-consumer-quota-card";

const quotas = [
  { consumer_id: "app-1", daily_limit: 1000, daily_used: 800, remaining: 200, exhausted: false },
  { consumer_id: "app-2", daily_limit: 100, daily_used: 100, remaining: 0, exhausted: true },
];

describe("APIConsumerQuotaCard", () => {
  it("renders with exhausted count", () => {
    const { container } = render(<APIConsumerQuotaCard quotas={quotas} appName="App" />);
    expect(container.textContent).toContain("Consumer Quotas");
    expect(container.textContent).toContain("1 exhausted");
    expect(container.textContent).toContain("800/1000");
  });
  it("shows empty", () => {
    const { container } = render(<APIConsumerQuotaCard quotas={[]} appName="App" />);
    expect(container.textContent).toContain("No consumer quotas");
  });
});
