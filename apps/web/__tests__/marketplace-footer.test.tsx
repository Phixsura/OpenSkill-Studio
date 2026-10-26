import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceFooter } from "@/components/marketplace-footer";

const mockSections = [
  { title: "Product", links: [
    { label: "Extensions", href: "/extensions" },
    { label: "Connectors", href: "/connectors" },
    { label: "Pricing", href: "/pricing" },
  ]},
  { title: "Developers", links: [
    { label: "Documentation", href: "/docs" },
    { label: "API Reference", href: "/api" },
    { label: "SDK", href: "/sdk" },
  ]},
  { title: "Company", links: [
    { label: "About", href: "/about" },
    { label: "Blog", href: "/blog" },
  ]},
  { title: "Support", links: [
    { label: "Help Center", href: "/help" },
    { label: "Contact", href: "/contact" },
  ]},
];

describe("MarketplaceFooter", () => {
  it("renders sections with links", () => {
    const { container } = render(
      <MarketplaceFooter sections={mockSections} version="3.2.1" copyright="© 2026 OpenSkill" />
    );
    expect(container.textContent).toContain("Product");
    expect(container.textContent).toContain("Extensions");
    expect(container.textContent).toContain("Developers");
    expect(container.textContent).toContain("Documentation");
    expect(container.textContent).toContain("Support");
  });

  it("shows version and copyright", () => {
    const { container } = render(
      <MarketplaceFooter sections={mockSections} version="3.2.1" copyright="© 2026 OpenSkill" />
    );
    expect(container.textContent).toContain("v3.2.1");
    expect(container.textContent).toContain("© 2026 OpenSkill");
  });

  it("shows legal links", () => {
    const { container } = render(
      <MarketplaceFooter sections={mockSections} version="1.0" copyright="©" />
    );
    expect(container.textContent).toContain("Status");
    expect(container.textContent).toContain("Privacy");
    expect(container.textContent).toContain("Terms");
  });
});
