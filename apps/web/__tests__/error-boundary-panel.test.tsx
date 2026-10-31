import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ErrorBoundaryPanel } from "@/components/error-boundary-panel";

const mockErrors = [
  { id: "e1", category: "runtime", message: "TypeError: null is not an object",
    actionTaken: "skip" as const, resolved: false, timestamp: "12:00" },
  { id: "e2", category: "timeout", message: "Request timed out after 30s",
    actionTaken: "retry" as const, resolved: false, timestamp: "12:05" },
  { id: "e3", category: "runtime", message: "SyntaxError",
    actionTaken: "halt" as const, resolved: true, timestamp: "11:50" },
];
const mockSummary = {
  total: 3, byCategory: { runtime: 2, timeout: 1 },
  circuitOpen: true, errorRate: 15,
};

describe("ErrorBoundaryPanel", () => {
  it("renders errors with summary", () => {
    const { container } = render(
      <ErrorBoundaryPanel errors={mockErrors} summary={mockSummary} />
    );
    expect(container.textContent).toContain("3 errors");
    expect(container.textContent).toContain("TypeError");
    expect(container.textContent).toContain("Circuit OPEN");
  });

  it("filters by category", () => {
    const { getByText, container } = render(
      <ErrorBoundaryPanel errors={mockErrors} summary={mockSummary} />
    );
    fireEvent.click(getByText("⏰ timeout (1)"));
    expect(container.textContent).toContain("Request timed out");
    expect(container.textContent).not.toContain("TypeError");
  });

  it("calls onResolve", () => {
    const onResolve = vi.fn();
    const { getAllByText } = render(
      <ErrorBoundaryPanel errors={mockErrors} summary={mockSummary} onResolve={onResolve} />
    );
    fireEvent.click(getAllByText("Resolve")[0]);
    expect(onResolve).toHaveBeenCalledWith("e1");
  });

  it("calls onResetCircuit", () => {
    const onReset = vi.fn();
    const { getByText } = render(
      <ErrorBoundaryPanel errors={mockErrors} summary={mockSummary} onResetCircuit={onReset} />
    );
    fireEvent.click(getByText("Reset"));
    expect(onReset).toHaveBeenCalled();
  });
});
