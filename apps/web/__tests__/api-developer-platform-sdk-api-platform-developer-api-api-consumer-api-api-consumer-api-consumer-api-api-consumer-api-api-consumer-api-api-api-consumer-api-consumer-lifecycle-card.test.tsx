import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-api-consumer-api-consumer-lifecycle-card";

describe("ConsumerLifecycleCard", () => {
  it("shows accounts", () => {
    const accounts = [{ id: "c1", name: "Acme Corp", status: "active", plan: "pro", createdAt: "2026-01" }];
    const { container } = render(<Card accounts={accounts} statusCounts={{ active: 5, suspended: 1 }} appName="App" />);
    expect(container.textContent).toContain("Consumer Lifecycle");
    expect(container.textContent).toContain("Acme Corp");
    expect(container.textContent).toContain("active: 5");
  });
  it("shows empty", () => {
    const { container } = render(<Card accounts={[]} statusCounts={{}} appName="App" />);
    expect(container.textContent).toContain("No consumers");
  });
});
