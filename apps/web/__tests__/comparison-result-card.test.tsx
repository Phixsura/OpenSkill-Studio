import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ComparisonResultCard } from "@/components/comparison-result-card";

describe("ComparisonResultCard", () => {
  const apps = [{ id: "a1", name: "App A", score: 85 }, { id: "a2", name: "App B", score: 92 }];
  it("renders", () => {
    const { container } = render(
      <ComparisonResultCard apps={apps} winner={apps[1]} shareableUrl="/compare" onShare={vi.fn()} />
    );
    expect(container.textContent).toContain("App B wins!");
    expect(container.textContent).toContain("92");
    expect(container.textContent).toContain("🏆");
  });
  it("share", () => {
    const fn = vi.fn();
    const { container } = render(
      <ComparisonResultCard apps={apps} winner={apps[1]} shareableUrl="" onShare={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Share Comparison")!);
    expect(fn).toHaveBeenCalled();
  });
});
