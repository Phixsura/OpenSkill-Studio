import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlatformHomePage } from "@/components/platform-home-page";

describe("PlatformHomePage", () => {
  it("renders platform home", () => {
    const { container } = render(
      <PlatformHomePage heroTitle="OpenSkill Marketplace" heroSubtitle="Discover apps"
        stats={{ apps: 5200, developers: 2000, downloads: 12500000, uptime: 99.99 }}
        featured={[{ id: "a1", name: "SuperApp", icon: "🚀", tagline: "Do more", rating: 4.8 }]}
        trending={[{ id: "a2", name: "HotApp", icon: "🔥", growth: 300 }]}
        categories={[{ id: "tools", name: "Tools", icon: "🔧", count: 320 }]}
        onSelectApp={vi.fn()} onSelectCategory={vi.fn()} onSearch={vi.fn()} />
    );
    expect(container.textContent).toContain("OpenSkill Marketplace");
    expect(container.textContent).toContain("5,200");
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("HotApp");
    expect(container.textContent).toContain("300%");
    expect(container.textContent).toContain("Tools");
  });
});
