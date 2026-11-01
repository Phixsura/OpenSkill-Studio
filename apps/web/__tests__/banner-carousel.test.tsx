import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BannerCarousel } from "@/components/banner-carousel";

describe("BannerCarousel", () => {
  const banners = [
    { index: 0, title: "New Feature!", subtitle: "Dark mode", cta_label: "Try it",
      cta_url: "/settings", bg_gradient: "from-blue-600 to-purple-600" },
    { index: 1, title: "SDK v3", subtitle: "Available now", cta_label: "Upgrade",
      cta_url: "/sdk", bg_gradient: "from-green-500 to-teal-600" },
  ];
  it("renders first banner", () => {
    const { container } = render(
      <BannerCarousel banners={banners} autoRotate={false} rotateIntervalMs={5000} onCtaClick={vi.fn()} />
    );
    expect(container.textContent).toContain("New Feature!");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("Try it");
  });
  it("cta click", () => {
    const fn = vi.fn();
    const { container } = render(
      <BannerCarousel banners={banners} autoRotate={false} rotateIntervalMs={5000} onCtaClick={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Try it")!);
    expect(fn).toHaveBeenCalledWith("/settings");
  });
});
