import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RateLimitVisualizer } from "@/components/rate-limit-visualizer";

const normalState = {
  key: "api-key-abc", allowed: true, remaining: 75, limit: 100,
  retryAfter: 0, violations: 0, requestsLastMinute: 25, requestsLastHour: 500,
};

const penalizedState = {
  key: "api-key-xyz", allowed: false, remaining: 0, limit: 100,
  retryAfter: 8, violations: 3, requestsLastMinute: 120, requestsLastHour: 2000,
};

describe("RateLimitVisualizer", () => {
  it("renders normal state with token bucket", () => {
    const { container } = render(<RateLimitVisualizer state={normalState} />);
    expect(container.textContent).toContain("75/100 tokens");
    expect(container.textContent).toContain("75%");
    expect(container.textContent).toContain("25");  // req/min
    expect(container.textContent).toContain("✓");
  });

  it("renders penalized state with violation info", () => {
    const { container } = render(<RateLimitVisualizer state={penalizedState} />);
    expect(container.textContent).toContain("0/100 tokens");
    expect(container.textContent).toContain("3 violations");
    expect(container.textContent).toContain("Penalty Level 3");
    expect(container.textContent).toContain("✕");
  });

  it("reset button calls handler", () => {
    const fn = vi.fn();
    const { container } = render(<RateLimitVisualizer state={normalState} onReset={fn} />);
    const resetBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Reset");
    if (resetBtn) fireEvent.click(resetBtn);
    expect(fn).toHaveBeenCalledWith("api-key-abc");
  });

  it("shows approaching max warning for high violations", () => {
    const { container } = render(<RateLimitVisualizer state={penalizedState} />);
    expect(container.textContent).toContain("approaching max");
  });
});
