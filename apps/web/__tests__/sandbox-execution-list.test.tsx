import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SandboxExecutionList } from "@/components/sandbox-execution-list";

describe("SandboxExecutionList", () => {
  it("shows executions", () => {
    const execs = [{ id: "e1", functionName: "sync", success: true, durationMs: 100, timestamp: "10:00" }];
    const { container } = render(<SandboxExecutionList executions={execs} total={50} />);
    expect(container.textContent).toContain("sync");
    expect(container.textContent).toContain("50 total");
  });
  it("empty state", () => {
    const { container } = render(<SandboxExecutionList executions={[]} total={0} />);
    expect(container.textContent).toContain("No executions");
  });
});
