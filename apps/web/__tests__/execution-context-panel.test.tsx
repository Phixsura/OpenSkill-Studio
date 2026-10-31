import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExecutionContextPanel } from "@/components/execution-context-panel";

const mockContexts = [
  { id: "c1", functionName: "processData", status: "completed" as const,
    durationMs: 145, memoryMb: 32, cpuMs: 80, inputKeys: ["data"], outputKeys: ["result"] },
  { id: "c2", functionName: "sendEmail", status: "running" as const,
    durationMs: 0, memoryMb: 0, cpuMs: 0, inputKeys: ["to"], outputKeys: [] },
  { id: "c3", functionName: "parseCSV", status: "failed" as const,
    durationMs: 50, memoryMb: 64, cpuMs: 30, error: "Invalid CSV format",
    inputKeys: ["file"], outputKeys: [] },
];
const mockStats = { total: 100, completed: 85, failed: 10, timeouts: 5, avgDurationMs: 120 };

describe("ExecutionContextPanel", () => {
  it("renders stats and contexts", () => {
    const { container } = render(
      <ExecutionContextPanel contexts={mockContexts} stats={mockStats} />
    );
    expect(container.textContent).toContain("processData");
    expect(container.textContent).toContain("85");
    expect(container.textContent).toContain("120ms");
  });

  it("shows error message", () => {
    const { container } = render(
      <ExecutionContextPanel contexts={mockContexts} stats={mockStats} />
    );
    expect(container.textContent).toContain("Invalid CSV format");
  });

  it("shows cancel for running", () => {
    const onCancel = vi.fn();
    const { getByText } = render(
      <ExecutionContextPanel contexts={mockContexts} stats={mockStats} onCancel={onCancel} />
    );
    fireEvent.click(getByText("Cancel"));
    expect(onCancel).toHaveBeenCalledWith("c2");
  });

  it("shows resource usage", () => {
    const { container } = render(
      <ExecutionContextPanel contexts={mockContexts} stats={mockStats} />
    );
    expect(container.textContent).toContain("RAM: 32MB");
    expect(container.textContent).toContain("CPU: 80ms");
  });
});
