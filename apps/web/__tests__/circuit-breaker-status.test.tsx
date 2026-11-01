import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CircuitBreakerStatus } from "@/components/circuit-breaker-status";

describe("CircuitBreakerStatus", () => {
  it("renders breakers", () => {
    const { container } = render(
      <CircuitBreakerStatus breakers={[
        { name: "database", state: "closed", failures: 0, totalTrips: 2 },
        { name: "payment", state: "open", failures: 5, totalTrips: 3 },
        { name: "email", state: "half_open", failures: 1, totalTrips: 1 },
      ]} />
    );
    expect(container.textContent).toContain("Circuit Breakers");
    expect(container.textContent).toContain("1 open");
    expect(container.textContent).toContain("database");
    expect(container.textContent).toContain("closed");
    expect(container.textContent).toContain("payment");
    expect(container.textContent).toContain("half open");
  });
});
