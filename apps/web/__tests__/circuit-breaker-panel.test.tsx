import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CircuitBreakerPanel } from "@/components/circuit-breaker-panel";

describe("CircuitBreakerPanel", () => {
  it("renders circuits", () => {
    const circuits = [
      { name: "API Gateway", state: "closed" },
      { name: "Webhook Service", state: "open" },
    ];
    const { container } = render(<CircuitBreakerPanel circuits={circuits} health="degraded" />);
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("closed");
    expect(container.textContent).toContain("open");
    expect(container.textContent).toContain("degraded");
  });
});
