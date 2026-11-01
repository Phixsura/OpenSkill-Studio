import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceAppPage } from "@/components/marketplace-app-page";

describe("MarketplaceAppPage", () => {
  it("renders app page", () => {
    const { container } = render(
      <MarketplaceAppPage
        app={{ name: "SuperApp", icon: "🚀", tagline: "Do more", description: "Great app",
               version: "2.0.0", pricing: "Free", tags: ["tools"] }}
        developer={{ name: "Alice", verified: true, appCount: 5 }}
        stats={{ installs: 25000, rating: 4.7, stars: "★★★★☆", reviewCount: 120 }}
        installed={false} cta="Install" onInstall={vi.fn()} />
    );
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("Do more");
    expect(container.textContent).toContain("25,000");
    expect(container.textContent).toContain("Install");
    expect(container.textContent).toContain("by Alice");
  });
});
