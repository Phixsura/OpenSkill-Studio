import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BatchExecutorPanel } from "@/components/batch-executor-panel";

const mockOps = [
  { opId: "o1", name: "create_user", status: "success" as const, durationMs: 50 },
  { opId: "o2", name: "send_email", status: "failed" as const, durationMs: 120, error: "SMTP error" },
  { opId: "o3", name: "log_event", status: "skipped" as const, durationMs: 0 },
];
const mockSummary = { status: "partial" as const, total: 3, succeeded: 1, failed: 1, skipped: 1, durationMs: 170 };

describe("BatchExecutorPanel", () => {
  it("renders summary", () => {
    const { container } = render(<BatchExecutorPanel operations={mockOps} summary={mockSummary} />);
    expect(container.textContent).toContain("partial");
    expect(container.textContent).toContain("170ms");
  });

  it("shows operations with status", () => {
    const { container } = render(<BatchExecutorPanel operations={mockOps} summary={mockSummary} />);
    expect(container.textContent).toContain("create_user");
    expect(container.textContent).toContain("SMTP error");
  });

  it("shows execute button when pending", () => {
    const onExecute = vi.fn();
    const pendingSummary = { ...mockSummary, status: "pending" as const };
    const { getByText } = render(<BatchExecutorPanel operations={[]} summary={pendingSummary} onExecute={onExecute} />);
    fireEvent.click(getByText("Execute"));
    expect(onExecute).toHaveBeenCalled();
  });

  it("shows stats grid", () => {
    const { container } = render(<BatchExecutorPanel operations={mockOps} summary={mockSummary} />);
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("1"); // succeeded and failed both 1
  });
});
