import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CircuitBreakerPanel } from "@/components/circuit-breaker-panel";

const mockCircuits = [
  { name: "api_gateway", state: "closed" as const, failureCount: 1,
    totalRequests: 500, totalFailures: 5, totalShortCircuits: 0, failureRate: 1.0 },
  { name: "db_connection", state: "open" as const, failureCount: 5,
    totalRequests: 100, totalFailures: 30, totalShortCircuits: 45, failureRate: 30.0 },
  { name: "cache_service", state: "half_open" as const, failureCount: 3,
    totalRequests: 200, totalFailures: 10, totalShortCircuits: 20, failureRate: 5.0 },
];

describe("CircuitBreakerPanel", () => {
  it("renders circuits with states", () => {
    const { container } = render(<CircuitBreakerPanel circuits={mockCircuits} />);
    expect(container.textContent).toContain("api_gateway");
    expect(container.textContent).toContain("Closed");
    expect(container.textContent).toContain("Open");
    expect(container.textContent).toContain("1 open");
  });

  it("shows failure stats", () => {
    const { container } = render(<CircuitBreakerPanel circuits={mockCircuits} />);
    expect(container.textContent).toContain("30%");
    expect(container.textContent).toContain("45");
  });

  it("calls onForceOpen", () => {
    const onForceOpen = vi.fn();
    const { getAllByText } = render(<CircuitBreakerPanel circuits={mockCircuits} onForceOpen={onForceOpen} />);
    fireEvent.click(getAllByText("Trip")[0]);
    expect(onForceOpen).toHaveBeenCalledWith("api_gateway");
  });

  it("calls onForceClose for open circuit", () => {
    const onForceClose = vi.fn();
    const { getAllByText } = render(<CircuitBreakerPanel circuits={mockCircuits} onForceClose={onForceClose} />);
    fireEvent.click(getAllByText("Reset")[0]);
    expect(onForceClose).toHaveBeenCalled();
  });
});
