import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CircuitBreakerPanel } from "@/components/circuit-breaker-panel";

describe("CircuitBreakerPanel", () => {
  const breakers = [
    { name: "api-gateway", state: "closed", failure_count: 1, failure_threshold: 5, recovery_timeout_sec: 30 },
    { name: "db-pool", state: "open", failure_count: 5, failure_threshold: 5, recovery_timeout_sec: 60 },
  ];
  it("renders", () => {
    const { container } = render(<CircuitBreakerPanel breakers={breakers} onReset={vi.fn()} />);
    expect(container.textContent).toContain("Circuit Breakers");
    expect(container.textContent).toContain("api-gateway");
    expect(container.textContent).toContain("🟢");
    expect(container.textContent).toContain("db-pool");
    expect(container.textContent).toContain("🔴");
    expect(container.textContent).toContain("Reset");
  });
  it("reset", () => {
    const fn = vi.fn();
    const { container } = render(<CircuitBreakerPanel breakers={breakers} onReset={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Reset")!);
    expect(fn).toHaveBeenCalledWith("db-pool");
  });
});
