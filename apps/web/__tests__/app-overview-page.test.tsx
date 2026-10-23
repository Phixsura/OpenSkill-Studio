import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppOverviewPage } from "@/components/app-overview-page";

describe("AppOverviewPage", () => {
  const header = { name: "SuperApp", icon: "🚀", tagline: "Do more", author: "Alice", verified: true, version: "2.0.0" };
  const stats = { downloads: 25000, rating: 4.7, stars: "★★★★☆", reviewCount: 120 };
  it("renders overview", () => {
    const { container } = render(
      <AppOverviewPage header={header} stats={stats} description="A powerful app"
        pricing="Free" tags={["productivity"]} installCta="Install" onInstall={vi.fn()} />
    );
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("Do more");
    expect(container.textContent).toContain("25,000");
    expect(container.textContent).toContain("★★★★☆");
    expect(container.textContent).toContain("Install");
    expect(container.textContent).toContain("productivity");
  });
});
