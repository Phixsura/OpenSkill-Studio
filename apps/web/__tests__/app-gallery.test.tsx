import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppGallery } from "@/components/app-gallery";

describe("AppGallery", () => {
  const collections = [{
    title: "Top Rated", description: "Best apps", icon: "⭐",
    apps: [{ id: "a1", name: "SuperApp", icon: "🚀" }],
  }];
  it("renders gallery", () => {
    const { container } = render(<AppGallery collections={collections} onSelectApp={vi.fn()} />);
    expect(container.textContent).toContain("Top Rated");
    expect(container.textContent).toContain("SuperApp");
  });
  it("select app", () => {
    const fn = vi.fn();
    const { container } = render(<AppGallery collections={collections} onSelectApp={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("a1");
  });
});
