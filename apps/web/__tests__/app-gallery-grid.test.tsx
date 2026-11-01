import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppGalleryGrid } from "@/components/app-gallery-grid";

describe("AppGalleryGrid", () => {
  it("renders gallery", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <AppGalleryGrid onSelect={onSelect} collections={[
        { id: "popular", title: "Most Popular", description: "Top apps", icon: "🔥",
          appCount: 2, featured: true, apps: [
            { name: "Slack", icon: "💬", rating: 4.8 },
            { name: "GitHub", icon: "🐙", rating: 4.9 },
          ]},
      ]} />
    );
    expect(container.textContent).toContain("Most Popular");
    expect(container.textContent).toContain("2 apps");
    expect(container.textContent).toContain("Featured");
    expect(container.textContent).toContain("Slack");
    expect(container.textContent).toContain("4.8");
    fireEvent.click(getByText("Most Popular"));
    expect(onSelect).toHaveBeenCalledWith("popular");
  });
});
