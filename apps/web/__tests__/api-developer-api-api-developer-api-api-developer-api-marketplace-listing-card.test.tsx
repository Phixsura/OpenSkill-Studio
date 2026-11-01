import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiMarketplaceListingCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-marketplace-listing-card";

const listings = [{ listing_id: "l1", app_name: "Super Analytics", description: "Best analytics tool", category: "analytics", pricing: "freemium", status: "published", installs: 5000, rating: 4.8 }];

describe("Card", () => {
  it("shows marketplace", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiMarketplaceListingCard listings={listings} appName="App" />);
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("Super Analytics");
    expect(container.textContent).toContain("freemium");
    expect(container.textContent).toContain("5,000 installs");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiMarketplaceListingCard listings={[]} appName="App" />);
    expect(container.textContent).toContain("No marketplace listings");
  });
});
