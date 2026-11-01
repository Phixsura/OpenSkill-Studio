import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ThrottleStatusPanel } from "@/components/throttle-status-panel";

const mockStates = [
  { extensionId: "ext-1", level: "none" as const, throughput: 1.0,
    reason: "normal", allowed: 1000, throttled: 0, hasOverride: false },
  { extensionId: "ext-2", level: "heavy" as const, throughput: 0.2,
    reason: "CPU 96%", allowed: 200, throttled: 800, hasOverride: false },
  { extensionId: "ext-3", level: "block" as const, throughput: 0.0,
    reason: "manual override", allowed: 0, throttled: 500, hasOverride: true },
];

describe("ThrottleStatusPanel", () => {
  it("renders throttle states", () => {
    const { container } = render(<ThrottleStatusPanel states={mockStates} />);
    expect(container.textContent).toContain("ext-1");
    expect(container.textContent).toContain("Normal");
    expect(container.textContent).toContain("Heavy");
    expect(container.textContent).toContain("Blocked");
  });

  it("shows throughput and counts", () => {
    const { container } = render(<ThrottleStatusPanel states={mockStates} />);
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("20%");
    expect(container.textContent).toContain("CPU 96%");
  });

  it("shows override indicator", () => {
    const { container } = render(<ThrottleStatusPanel states={mockStates} />);
    expect(container.textContent).toContain("override");
  });

  it("calls onClearOverride for overridden", () => {
    const onClear = vi.fn();
    const { getByText } = render(<ThrottleStatusPanel states={mockStates} onClearOverride={onClear} />);
    fireEvent.click(getByText("Clear"));
    expect(onClear).toHaveBeenCalledWith("ext-3");
  });
});
