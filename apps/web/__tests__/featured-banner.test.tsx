import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeaturedBanner } from "@/components/featured-banner";

describe("FeaturedBanner", () => {
  it("renders banner", () => {
    const { container } = render(
      <FeaturedBanner title="SDK v3!" subtitle="New features" ctaLabel="Learn More"
        ctaHref="/blog" backgroundColor="#3B82F6" icon="🎉" onDismiss={vi.fn()} />
    );
    expect(container.textContent).toContain("SDK v3!");
    expect(container.textContent).toContain("New features");
    expect(container.textContent).toContain("Learn More");
  });
  it("dismiss", () => {
    const fn = vi.fn();
    const { container } = render(
      <FeaturedBanner title="X" subtitle="Y" ctaLabel="Z" ctaHref="#"
        backgroundColor="#000" icon="🎉" onDismiss={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "✕")!);
    expect(fn).toHaveBeenCalled();
  });
});
