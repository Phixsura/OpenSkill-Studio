import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppCardGrid } from "@/components/app-card-grid";

describe("AppCardGrid", () => {
  const cards = [
    { id: "a1", name: "SuperApp", shortDescription: "Great tool", icon: "🚀",
      stars: "★★★★☆", downloadsDisplay: "25K", category: "tools", verified: true, pricing: "$9/mo" },
  ];
  it("renders cards", () => {
    const { container } = render(<AppCardGrid cards={cards} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("★★★★☆");
    expect(container.textContent).toContain("25K");
    expect(container.textContent).toContain("$9/mo");
  });
  it("select click", () => {
    const fn = vi.fn();
    const { container } = render(<AppCardGrid cards={cards} onSelect={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("a1");
  });
});
