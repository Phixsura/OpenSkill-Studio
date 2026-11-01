import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AutomationTriggerList } from "@/components/automation-trigger-list";

const triggers = [
  { triggerId: "t1", name: "Daily Sync", eventType: "schedule", enabled: true, fireCount: 42 },
  { triggerId: "t2", name: "PR Hook", eventType: "webhook", enabled: false, fireCount: 0 },
];

describe("AutomationTriggerList", () => {
  it("renders triggers", () => {
    const { container } = render(<AutomationTriggerList triggers={triggers} />);
    expect(container.textContent).toContain("Daily Sync");
    expect(container.textContent).toContain("fired 42×");
  });
  it("fires trigger", () => {
    const fn = vi.fn();
    const { container } = render(<AutomationTriggerList triggers={triggers} onFire={fn} />);
    const fireBtns = Array.from(container.querySelectorAll("button")).filter(b => b.textContent === "Fire");
    fireEvent.click(fireBtns[0]);
    expect(fn).toHaveBeenCalledWith("t1");
  });
});
