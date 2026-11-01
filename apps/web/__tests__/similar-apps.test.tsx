import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SimilarApps } from "@/components/similar-apps";

describe("SimilarApps", () => {
  const apps = [
    { id: "a2", name: "Code Linter", icon: "🔍", category: "tools", rating: 4.5 },
    { id: "a4", name: "IDE", icon: "💻", category: "tools", rating: 4.8 },
  ];
  it("renders similar apps", () => {
    const { container } = render(<SimilarApps apps={apps} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Similar Apps");
    expect(container.textContent).toContain("Code Linter");
    expect(container.textContent).toContain("IDE");
  });
  it("selects app", () => {
    const fn = vi.fn();
    const { container } = render(<SimilarApps apps={apps} onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("a2");
  });
});
