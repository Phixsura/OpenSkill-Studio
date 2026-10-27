import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ABTestResultsCard } from "@/components/ab-test-results-card";

const result = {
  testId: "ab-1", field: "title",
  variants: [
    { id: "a", name: "Original", impressions: 1000, conversions: 50, rate: 5.0 },
    { id: "b", name: "New Title", impressions: 1000, conversions: 75, rate: 7.5 },
  ],
};

describe("ABTestResultsCard", () => {
  it("renders results with winner", () => {
    const { container } = render(<ABTestResultsCard result={result} />);
    expect(container.textContent).toContain("A/B Test: title");
    expect(container.textContent).toContain("7.5%");
    expect(container.textContent).toContain("👑");
  });
  it("stop test", () => {
    const fn = vi.fn();
    const { container } = render(<ABTestResultsCard result={result} onStop={fn} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Stop"));
    if (btn) fireEvent.click(btn);
    expect(fn).toHaveBeenCalledWith("ab-1");
  });
});
