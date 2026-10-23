import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CircuitBreakerStatus } from "@/components/circuit-breaker-status";

describe("CircuitBreakerStatus", () => {
  it("renders closed state", () => {
    const { container } = render(
      <CircuitBreakerStatus state="closed" failures={1} threshold={5} recoveryTimeoutS={30} />
    );
    expect(container.textContent).toContain("closed");
    expect(container.textContent).toContain("1/5");
    expect(container.textContent).toContain("🟢");
  });
  it("renders open state", () => {
    const { container } = render(
      <CircuitBreakerStatus state="open" failures={5} threshold={5} recoveryTimeoutS={30} />
    );
    expect(container.textContent).toContain("open");
    expect(container.textContent).toContain("🔴");
  });
});
