import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BreadcrumbNav } from "@/components/breadcrumb-nav";

describe("BreadcrumbNav", () => {
  const crumbs = [
    { label: "Home", path: "/", active: false },
    { label: "Apps", path: "/apps", active: false },
    { label: "Settings", path: "/apps/a1/settings", active: true },
  ];
  it("renders", () => {
    const { container } = render(<BreadcrumbNav breadcrumbs={crumbs} onNavigate={vi.fn()} />);
    expect(container.textContent).toContain("Home");
    expect(container.textContent).toContain("Apps");
    expect(container.textContent).toContain("Settings");
  });
  it("navigate", () => {
    const fn = vi.fn();
    const { container } = render(<BreadcrumbNav breadcrumbs={crumbs} onNavigate={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("/");
  });
});
