import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppSpotlightHero } from "@/components/app-spotlight-hero";

describe("AppSpotlightHero", () => {
  it("renders", () => {
    const { container } = render(
      <AppSpotlightHero appName="Auth SDK" category="security" rating={4.8}
        installCount={5000} curatorNote="Best auth solution"
        highlights={["⭐ 4.8 rating", "📥 5,000 installs"]} week="2026-W43"
        onInstall={vi.fn()} onLearnMore={vi.fn()} />
    );
    expect(container.textContent).toContain("App of the Week");
    expect(container.textContent).toContain("Auth SDK");
    expect(container.textContent).toContain("Best auth solution");
    expect(container.textContent).toContain("⭐ 4.8 rating");
    expect(container.textContent).toContain("Install Free");
  });
  it("install", () => {
    const fn = vi.fn();
    const { container } = render(
      <AppSpotlightHero appName="X" category="x" rating={4} installCount={0}
        curatorNote="" highlights={[]} week="W1" onInstall={fn} onLearnMore={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Install Free")!);
    expect(fn).toHaveBeenCalled();
  });
});
