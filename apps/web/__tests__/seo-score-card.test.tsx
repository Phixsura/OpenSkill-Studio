import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SeoScoreCard } from "@/components/seo-score-card";

describe("SeoScoreCard", () => {
  it("perfect", () => {
    const { container } = render(<SeoScoreCard score={100} grade="A" issues={[]} onFix={vi.fn()} />);
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("100/100");
    expect(container.textContent).toContain("No SEO issues");
  });
  it("with issues", () => {
    const issues = [{ field: "title", issue: "Too short", impact: -15 }];
    const fn = vi.fn();
    const { container } = render(<SeoScoreCard score={85} grade="B" issues={issues} onFix={fn} />);
    expect(container.textContent).toContain("Too short");
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Fix")!);
    expect(fn).toHaveBeenCalledWith("title");
  });
});
