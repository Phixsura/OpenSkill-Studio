import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogCategoryCard from "../src/components/changelog-category-card";

const categories = [
  { category: "Features", emoji: "✨", count: 15 },
  { category: "Fixes", emoji: "🐛", count: 8 },
  { category: "Breaking", emoji: "💥", count: 2 },
];

describe("ChangelogCategoryCard", () => {
  it("renders header and total", () => {
    const { container } = render(<ChangelogCategoryCard categories={categories} appName="App" />);
    expect(container.textContent).toContain("Changelog Categories");
    expect(container.textContent).toContain("25 entries");
  });

  it("shows category names with emoji", () => {
    const { container } = render(<ChangelogCategoryCard categories={categories} appName="App" />);
    expect(container.textContent).toContain("✨");
    expect(container.textContent).toContain("Features");
    expect(container.textContent).toContain("🐛");
  });

  it("shows counts", () => {
    const { container } = render(<ChangelogCategoryCard categories={categories} appName="App" />);
    expect(container.textContent).toContain("15");
    expect(container.textContent).toContain("8");
  });

  it("shows empty state", () => {
    const { container } = render(<ChangelogCategoryCard categories={[]} appName="App" />);
    expect(container.textContent).toContain("No categories");
  });
});
