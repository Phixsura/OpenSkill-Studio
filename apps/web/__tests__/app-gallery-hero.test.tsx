import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppGalleryHero } from "@/components/app-gallery-hero";

describe("AppGalleryHero", () => {
  const sections = [{ id: "featured", title: "Featured", icon: "⭐",
    apps: [{ id: "a1", name: "Auth SDK" }] }];
  const collections = [{ id: "c1", title: "Security", description: "Security apps", app_count: 5, icon: "🔒" }];
  it("renders", () => {
    const { container } = render(
      <AppGalleryHero sections={sections} collections={collections}
        onAppClick={vi.fn()} onCollectionClick={vi.fn()} />
    );
    expect(container.textContent).toContain("⭐");
    expect(container.textContent).toContain("Featured");
    expect(container.textContent).toContain("Auth SDK");
    expect(container.textContent).toContain("Security");
    expect(container.textContent).toContain("5 apps");
  });
  it("app click", () => {
    const fn = vi.fn();
    const { container } = render(
      <AppGalleryHero sections={sections} collections={collections}
        onAppClick={fn} onCollectionClick={vi.fn()} />
    );
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("a1");
  });
});
