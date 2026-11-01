import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppGalleryToolbar } from "@/components/app-gallery-toolbar";

describe("AppGalleryToolbar", () => {
  const sortOptions = [{ id: "popular", label: "Popular", icon: "🔥" }];
  const viewModes = [{ id: "grid", label: "Grid", icon: "▦" }, { id: "list", label: "List", icon: "☰" }];
  it("renders", () => {
    const { container } = render(
      <AppGalleryToolbar sortOptions={sortOptions} viewModes={viewModes}
        activeSort="popular" activeView="grid" totalResults={500}
        onSortChange={vi.fn()} onViewChange={vi.fn()} />
    );
    expect(container.textContent).toContain("500 apps");
  });
  it("switches view", () => {
    const fn = vi.fn();
    const { container } = render(
      <AppGalleryToolbar sortOptions={sortOptions} viewModes={viewModes}
        activeSort="popular" activeView="grid" totalResults={0}
        onSortChange={vi.fn()} onViewChange={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[1]); // list
    expect(fn).toHaveBeenCalledWith("list");
  });
});
