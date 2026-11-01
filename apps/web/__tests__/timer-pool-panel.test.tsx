import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TimerPoolPanel } from "@/components/timer-pool-panel";

const mockTimers = [
  { timerId: "t1", timerType: "interval" as const, callbackName: "poll", delayMs: 5000,
    state: "active" as const, fireCount: 10, maxFires: 0 },
  { timerId: "t2", timerType: "timeout" as const, callbackName: "delayed_init", delayMs: 30000,
    state: "active" as const, fireCount: 0, maxFires: 0 },
  { timerId: "t3", timerType: "interval" as const, callbackName: "cleanup", delayMs: 60000,
    state: "fired" as const, fireCount: 5, maxFires: 5 },
];

describe("TimerPoolPanel", () => {
  it("renders timers", () => {
    const { container } = render(<TimerPoolPanel timers={mockTimers} activeCount={2} />);
    expect(container.textContent).toContain("poll");
    expect(container.textContent).toContain("interval");
    expect(container.textContent).toContain("5.0s");
    expect(container.textContent).toContain("2 active");
  });

  it("shows fire count for intervals", () => {
    const { container } = render(<TimerPoolPanel timers={mockTimers} activeCount={2} />);
    expect(container.textContent).toContain("×10");
    expect(container.textContent).toContain("5/5");
  });

  it("calls onCancel", () => {
    const onCancel = vi.fn();
    const { getAllByText } = render(<TimerPoolPanel timers={mockTimers} activeCount={2} onCancel={onCancel} />);
    fireEvent.click(getAllByText("Cancel")[0]);
    expect(onCancel).toHaveBeenCalledWith("t1");
  });

  it("calls onClearAll", () => {
    const onClearAll = vi.fn();
    const { getByText } = render(<TimerPoolPanel timers={mockTimers} activeCount={2} onClearAll={onClearAll} />);
    fireEvent.click(getByText("Clear All"));
    expect(onClearAll).toHaveBeenCalled();
  });
});
