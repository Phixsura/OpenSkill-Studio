import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import AppListingCard from "../src/components/app-listing-card";

const listings = [
  {
    listing_id: "l1",
    name: "Analytics Tool",
    description: "Track everything",
    category: "tools",
    status: "published" as const,
    install_count: 1500,
    avg_rating: 4.5,
    rating_count: 30,
    tags: ["analytics", "data"],
  },
  {
    listing_id: "l2",
    name: "Chat Widget",
    description: "Live chat",
    category: "ui",
    status: "draft" as const,
    install_count: 0,
    avg_rating: 0,
    rating_count: 0,
    tags: [],
  },
];

describe("AppListingCard", () => {
  it("renders header", () => {
    const { container } = render(<AppListingCard listings={listings} appName="My App" />);
    expect(container.textContent).toContain("App Listings");
  });

  it("shows published count", () => {
    const { container } = render(<AppListingCard listings={listings} appName="App" />);
    expect(container.textContent).toContain("1 published");
  });

  it("renders listing names and descriptions", () => {
    const { container } = render(<AppListingCard listings={listings} appName="App" />);
    expect(container.textContent).toContain("Analytics Tool");
    expect(container.textContent).toContain("Track everything");
  });

  it("shows ratings and installs", () => {
    const { container } = render(<AppListingCard listings={listings} appName="App" />);
    expect(container.textContent).toContain("4.5");
    expect(container.textContent).toContain("1.5K installs");
  });

  it("shows tags", () => {
    const { container } = render(<AppListingCard listings={listings} appName="App" />);
    expect(container.textContent).toContain("analytics");
    expect(container.textContent).toContain("data");
  });

  it("shows empty state", () => {
    const { container } = render(<AppListingCard listings={[]} appName="App" />);
    expect(container.textContent).toContain("No listings");
  });
});
