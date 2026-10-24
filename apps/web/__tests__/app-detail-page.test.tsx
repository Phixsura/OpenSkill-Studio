import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppDetailPage } from "@/components/app-detail-page";

describe("AppDetailPage", () => {
  it("renders detail", () => {
    const { container } = render(
      <AppDetailPage
        header={{ name: "SuperApp", icon: "🚀", version: "2.0.0", author: "Alice", verified: true, tagline: "Do more" }}
        description="A great app" stats={{ installs: 25000, rating: 4.5, stars: "★★★★☆", reviewCount: 120 }}
        pricing="Free" installed={false} cta="Install" tags={["tools"]}
        similarApps={[{ id: "s1", name: "Similar", icon: "📦" }]}
        onInstall={vi.fn()} onSelectSimilar={vi.fn()} />
    );
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("Do more");
    expect(container.textContent).toContain("25,000");
    expect(container.textContent).toContain("Install");
    expect(container.textContent).toContain("Similar");
  });
});
