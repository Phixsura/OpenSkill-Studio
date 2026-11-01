import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperMarketplaceCard from "../src/components/api-developer-marketplace-card";

const listings = [
  { listing_id: "l1", name: "Auth Plugin", category: "auth", install_count: 500, rating: 4.5, published: true },
  { listing_id: "l2", name: "Draft Plugin", category: "tools", install_count: 0, rating: 0, published: false },
];

describe("APIDeveloperMarketplaceCard", () => {
  it("shows listings", () => {
    const { container } = render(<APIDeveloperMarketplaceCard listings={listings} appName="App" />);
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("1/2 published");
    expect(container.textContent).toContain("Auth Plugin");
    expect(container.textContent).toContain("500 installs");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperMarketplaceCard listings={[]} appName="App" />);
    expect(container.textContent).toContain("No marketplace listings");
  });
});
