import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExecutionHistoryList } from "@/components/execution-history-list";

const EXECS = [
  { functionName: "sync", success: true, durationMs: 100, trigger: "event", timestamp: "10:00" },
  { functionName: "sync", success: false, durationMs: 5000, trigger: "manual", timestamp: "10:01", error: "timeout" },
];

describe("ExecutionHistoryList", () => {
  it("shows executions", () => {
    const { container } = render(<ExecutionHistoryList executions={EXECS} />);
    expect(container.textContent).toContain("sync");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("❌");
  });
  it("empty state", () => {
    const { container } = render(<ExecutionHistoryList executions={[]} />);
    expect(container.textContent).toContain("No executions");
  });
});
