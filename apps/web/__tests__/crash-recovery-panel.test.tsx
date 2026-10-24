import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CrashRecoveryPanel } from "@/components/crash-recovery-panel";

describe("CrashRecoveryPanel", () => {
  const steps = [
    { step: 1, action: "Restart with more memory", status: "completed" },
    { step: 2, action: "Analyze memory leak", status: "pending" },
  ];
  it("renders", () => {
    const { container } = render(
      <CrashRecoveryPanel crashType="oom" steps={steps} autoRecovery={true}
        onExecuteStep={vi.fn()} onRollback={vi.fn()} />
    );
    expect(container.textContent).toContain("Crash Recovery");
    expect(container.textContent).toContain("oom");
    expect(container.textContent).toContain("💾");
    expect(container.textContent).toContain("Auto");
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("Execute");
    expect(container.textContent).toContain("Rollback");
  });
  it("execute step", () => {
    const fn = vi.fn();
    const { container } = render(
      <CrashRecoveryPanel crashType="oom" steps={steps} autoRecovery={false}
        onExecuteStep={fn} onRollback={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Execute")!);
    expect(fn).toHaveBeenCalledWith(2);
  });
});
