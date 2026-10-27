import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ErrorTrackingDashboard } from "@/components/error-tracking-dashboard";

const groups = [
  { fingerprint: "fp1", errorType: "TypeError", message: "undefined is not a function", count: 42, lastSeen: Date.now(), resolved: false },
  { fingerprint: "fp2", errorType: "RangeError", message: "Index out of bounds", count: 5, lastSeen: Date.now(), resolved: false },
];

describe("ErrorTrackingDashboard", () => {
  it("renders error groups", () => {
    const { container } = render(<ErrorTrackingDashboard groups={groups} />);
    expect(container.textContent).toContain("TypeError");
    expect(container.textContent).toContain("42×");
    expect(container.textContent).toContain("47 total");
  });
  it("resolve error", () => {
    const fn = vi.fn();
    const { container } = render(<ErrorTrackingDashboard groups={groups} onResolve={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[0]);
    expect(fn).toHaveBeenCalledWith("fp1");
  });
});
