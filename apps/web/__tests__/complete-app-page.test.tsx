import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CompleteAppPage } from "@/components/complete-app-page";

describe("CompleteAppPage", () => {
  it("renders complete page", () => {
    const { container } = render(
      <CompleteAppPage
        app={{ name: "SuperApp", icon: "🚀", tagline: "Do more", description: "Great",
               version: "2.0.0", pricing: "Free", tags: ["tools"] }}
        developer={{ name: "Alice", verified: true }}
        stats={{ installs: 25000, rating: 4.7, stars: "★★★★☆", reviewCount: 120 }}
        topReviews={[{ rating: 5, title: "Amazing!", author: "Bob" }]}
        similarApps={[{ id: "s1", name: "Similar", icon: "📦" }]}
        recentChangelog={[{ version: "2.0.0", title: "Major update" }]}
        installed={false} cta="Install" onInstall={vi.fn()} onSelectSimilar={vi.fn()} />
    );
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("25,000");
    expect(container.textContent).toContain("Amazing!");
    expect(container.textContent).toContain("Major update");
    expect(container.textContent).toContain("Similar");
  });
});
