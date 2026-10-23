import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformFooter } from "@/components/platform-footer";

describe("PlatformFooter", () => {
  const props = {
    brand: { name: "OpenSkill", tagline: "The Developer Platform" },
    sections: [
      { title: "Product", links: [{ label: "Marketplace", url: "/marketplace" }] },
      { title: "Developers", links: [{ label: "Docs", url: "/docs" }] },
    ],
    social: [{ platform: "github", url: "https://github.com/openskill", icon: "🐙" }],
    copyright: "© 2026 OpenSkill. All rights reserved.",
  };
  it("renders complete footer", () => {
    const { container } = render(<PlatformFooter {...props} />);
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("The Developer Platform");
    expect(container.textContent).toContain("Product");
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("Developers");
    expect(container.textContent).toContain("Docs");
    expect(container.textContent).toContain("🐙");
    expect(container.textContent).toContain("© 2026");
  });
});
