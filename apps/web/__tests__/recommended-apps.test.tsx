import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RecommendedApps } from "@/components/recommended-apps";

const APPS = [{ name: "Cool App", category: "connector", installCount: 42, description: "Great connector" }];

describe("RecommendedApps", () => {
  it("shows title", () => {
    const { container } = render(<RecommendedApps apps={APPS} />);
    expect(container.textContent).toContain("Recommended");
  });
  it("shows apps", () => {
    const { container } = render(<RecommendedApps apps={APPS} />);
    expect(container.textContent).toContain("Cool App");
    expect(container.textContent).toContain("42 installs");
  });
  it("returns null when empty", () => {
    const { container } = render(<RecommendedApps apps={[]} />);
    expect(container.innerHTML).toBe("");
  });
});
