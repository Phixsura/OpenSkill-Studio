import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CircuitBreakerStatus } from "@/components/circuit-breaker-status";

describe("CircuitBreakerStatus", () => {
  it("renders breakers", () => {
    const { container } = render(
      <CircuitBreakerStatus services={[
        { name: "Payment API", state: "closed", failures: 0, threshold: 5 },
        { name: "Email Service", state: "open", failures: 5, threshold: 5 },
        { name: "Search", state: "half_open", failures: 3, threshold: 5 },
      ]} />
    );
    expect(container.textContent).toContain("Circuit Breakers");
    expect(container.textContent).toContain("Payment API");
    expect(container.textContent).toContain("closed");
    expect(container.textContent).toContain("open");
    expect(container.textContent).toContain("half open");
  });
});
