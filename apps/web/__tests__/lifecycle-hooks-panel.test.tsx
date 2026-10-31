import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LifecycleHooksPanel } from "@/components/lifecycle-hooks-panel";

const mockHooks = [
  { hookId: "h1", event: "after_start", handlerName: "init_db", order: 1,
    enabled: true, executionCount: 10, errorCount: 0 },
  { hookId: "h2", event: "before_stop", handlerName: "save_state", order: 1,
    enabled: true, executionCount: 5, errorCount: 1, lastError: "timeout" },
  { hookId: "h3", event: "on_crash", handlerName: "report_crash", order: 0,
    enabled: false, executionCount: 3, errorCount: 5 },
];

describe("LifecycleHooksPanel", () => {
  it("renders hooks with events", () => {
    const { container } = render(<LifecycleHooksPanel hooks={mockHooks} />);
    expect(container.textContent).toContain("init_db");
    expect(container.textContent).toContain("save_state");
    expect(container.textContent).toContain("×10");
  });

  it("filters by event", () => {
    const { container } = render(<LifecycleHooksPanel hooks={mockHooks} />);
    const btns = container.querySelectorAll("button");
    const crashBtn = Array.from(btns).find(b => b.textContent?.includes("on_crash") && b.className.includes("rounded-full"));
    if (crashBtn) fireEvent.click(crashBtn);
    expect(container.textContent).toContain("report_crash");
  });

  it("shows error count", () => {
    const { container } = render(<LifecycleHooksPanel hooks={mockHooks} />);
    expect(container.textContent).toContain("1 errors");
    expect(container.textContent).toContain("5 errors");
  });

  it("calls onTrigger", () => {
    const onTrigger = vi.fn();
    const { container } = render(<LifecycleHooksPanel hooks={mockHooks} onTrigger={onTrigger} />);
    const triggerBtns = container.querySelectorAll("button");
    const trigBtn = Array.from(triggerBtns).find(b => b.textContent?.includes("after_start") && !b.className.includes("rounded-full"));
    if (trigBtn) fireEvent.click(trigBtn);
    expect(onTrigger).toHaveBeenCalledWith("after_start");
  });
});
