import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BreadcrumbBar } from "@/components/breadcrumb-bar";

describe("BreadcrumbBar", () => {
  it("renders breadcrumbs", () => {
    const onNav = vi.fn();
    const { container, getByText } = render(
      <BreadcrumbBar onNavigate={onNav} crumbs={[
        { label: "Home", path: "/", active: false },
        { label: "Apps", path: "/apps", active: false },
        { label: "Settings", path: "/apps/settings", active: true },
      ]} />
    );
    expect(container.textContent).toContain("Home");
    expect(container.textContent).toContain("Apps");
    expect(container.textContent).toContain("Settings");
    fireEvent.click(getByText("Home"));
    expect(onNav).toHaveBeenCalledWith("/");
  });
});
