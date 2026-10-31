import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FavoritesPanel } from "@/components/favorites-panel";

const favs = [
  { extensionId: "ext-1", name: "Slack Bot", icon: "🤖", pinned: true, accessCount: 42 },
  { extensionId: "ext-2", name: "GitHub Sync", icon: "🐙", pinned: false, accessCount: 10 },
];

describe("FavoritesPanel", () => {
  it("renders favorites", () => {
    const { container } = render(<FavoritesPanel favorites={favs} />);
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("×42");
    expect(container.textContent).toContain("📌");
  });
  it("calls onRemove", () => {
    const fn = vi.fn();
    const { container } = render(<FavoritesPanel favorites={favs} onRemove={fn} />);
    const del = container.querySelectorAll("button");
    const removeBtn = Array.from(del).find(b => b.textContent === "✕");
    if (removeBtn) fireEvent.click(removeBtn);
    expect(fn).toHaveBeenCalled();
  });
});
