import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BreadcrumbNav } from "@/components/breadcrumb-nav";

describe("BreadcrumbNav", () => {
  it("renders breadcrumbs", () => {
    const crumbs = [
      { label: "Home", url: "/", active: false },
      { label: "Marketplace", url: "/marketplace", active: false },
      { label: "SuperApp", url: null, active: true },
    ];
    const { container } = render(<BreadcrumbNav crumbs={crumbs} />);
    expect(container.textContent).toContain("Home");
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("SuperApp");
    const links = container.querySelectorAll("a");
    expect(links.length).toBe(2); // Home + Marketplace (SuperApp is active, not a link)
  });
});
