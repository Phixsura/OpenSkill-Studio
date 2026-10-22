import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppBreadcrumbs } from "@/components/app-breadcrumbs";

describe("AppBreadcrumbs", () => {
  it("shows crumbs", () => {
    const { container } = render(<AppBreadcrumbs crumbs={[{ label: "Apps", href: "/apps" }, { label: "My App" }]} />);
    expect(container.textContent).toContain("Apps");
    expect(container.textContent).toContain("My App");
  });
  it("has links", () => {
    const { container } = render(<AppBreadcrumbs crumbs={[{ label: "Home", href: "/" }]} />);
    expect(container.querySelector("a")).toBeTruthy();
  });
});
