import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CircuitDashboardCard from "../src/components/api-developer-platform-sdk-consumer-api-circuit-dashboard-card";

describe("CircuitDashboardCard", () => {
  it("renders title and circuits", () => {
    const { container } = render(<CircuitDashboardCard />);
    expect(container.textContent).toContain("Circuit Breakers");
    expect(container.textContent).toContain("ep-auth");
    expect(container.textContent).toContain("ep-payments");
  });

  it("shows state counts", () => {
    const { container } = render(<CircuitDashboardCard />);
    expect(container.textContent).toContain("2 closed");
    expect(container.textContent).toContain("1 open");
    expect(container.textContent).toContain("1 half-open");
  });
});
