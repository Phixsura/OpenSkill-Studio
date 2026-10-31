import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionGallery } from "@/components/extension-gallery";

const mockExts = [
  { id: "1", name: "Slack Bot", icon: "💬", author: "alice", description: "Slack integration", rating: 4.8, downloads: 15000, category: "messaging", featured: true },
  { id: "2", name: "Dark Theme", icon: "🎨", author: "bob", description: "Beautiful dark theme", rating: 4.9, downloads: 8000, category: "themes", featured: false },
  { id: "3", name: "Git Sync", icon: "🐙", author: "carol", description: "Sync with Git", rating: 4.2, downloads: 5000, category: "tools", featured: true },
];

describe("ExtensionGallery", () => {
  it("renders extensions and categories", () => {
    const { container } = render(
      <ExtensionGallery extensions={mockExts} categories={["messaging", "themes", "tools"]} />
    );
    expect(container.textContent).toContain("Extension Gallery");
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Dark Theme");
    expect(container.textContent).toContain("3 extensions");
  });

  it("filters by category", () => {
    const { container, getByText } = render(
      <ExtensionGallery extensions={mockExts} categories={["messaging", "themes", "tools"]} />
    );
    fireEvent.click(getByText("themes"));
    expect(container.textContent).toContain("1 extensions");
  });

  it("calls onSelect", () => {
    const onSelect = vi.fn();
    const { getAllByText } = render(
      <ExtensionGallery extensions={mockExts} categories={[]} onSelect={onSelect} />
    );
    // Click on a non-featured card
    fireEvent.click(getAllByText("Dark Theme")[0]);
    expect(onSelect).toHaveBeenCalledWith("2");
  });
});
