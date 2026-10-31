import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BreadcrumbNav } from "@/components/breadcrumb-nav";

describe("BreadcrumbNav", () => {
  const trail = [
    { label: "Home", href: "/", is_current: false },
    { label: "Marketplace", href: "/marketplace", is_current: false },
    { label: "My App", href: null, is_current: true },
  ];
  it("renders links and current", () => {
    const { container } = render(<BreadcrumbNav trail={trail} />);
    const links = container.querySelectorAll("a");
    expect(links.length).toBe(2);
    expect(links[0].getAttribute("href")).toBe("/");
    expect(container.textContent).toContain("My App");
  });
  it("shows separators", () => {
    const { container } = render(<BreadcrumbNav trail={trail} />);
    expect(container.textContent).toContain("/");
  });
});
