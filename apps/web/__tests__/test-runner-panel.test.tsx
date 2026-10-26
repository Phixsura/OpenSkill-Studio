import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TestRunnerPanel } from "@/components/test-runner-panel";

const mockTests = [
  { name: "test_add", result: "passed" as const, durationMs: 5, assertionCount: 3 },
  { name: "test_divide", result: "failed" as const, durationMs: 8, errorMessage: "Division by zero", assertionCount: 1 },
  { name: "test_slow", result: "skipped" as const, durationMs: 0, assertionCount: 0 },
];
const mockSummary = { suitesRun: 1, totalTests: 3, passed: 1, failed: 1, skipped: 1, passRate: 50.0, totalAssertions: 4 };

describe("TestRunnerPanel", () => {
  it("renders test results", () => {
    const { container } = render(
      <TestRunnerPanel tests={mockTests} summary={mockSummary} isRunning={false} />
    );
    expect(container.textContent).toContain("test_add");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("4");
  });

  it("filters by result", () => {
    const { getByText, container } = render(
      <TestRunnerPanel tests={mockTests} summary={mockSummary} isRunning={false} />
    );
    fireEvent.click(getByText("failed"));
    expect(container.textContent).toContain("test_divide");
    expect(container.textContent).not.toContain("test_add");
  });

  it("calls onRun", () => {
    const onRun = vi.fn();
    const { getByText } = render(
      <TestRunnerPanel tests={[]} summary={mockSummary} isRunning={false} onRun={onRun} />
    );
    fireEvent.click(getByText("Run Tests"));
    expect(onRun).toHaveBeenCalled();
  });

  it("shows running state", () => {
    const { container } = render(
      <TestRunnerPanel tests={[]} summary={mockSummary} isRunning={true} />
    );
    expect(container.textContent).toContain("Running...");
  });
});
