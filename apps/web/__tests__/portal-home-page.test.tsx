import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PortalHomePage } from "@/components/portal-home-page";

describe("PortalHomePage", () => {
  it("renders portal", () => {
    const onNav = vi.fn();
    const { container, getByText } = render(
      <PortalHomePage greeting="Welcome back, Alice!" onNavigate={onNav}
        statsBar={[
          { icon: "📱", value: "5", label: "Apps" },
          { icon: "📡", value: "150,000", label: "API Today" },
        ]}
        quickLinks={[
          { label: "Create App", icon: "📱", path: "/apps/new" },
          { label: "API Docs", icon: "📚", path: "/docs/api" },
        ]} />
    );
    expect(container.textContent).toContain("Welcome back, Alice!");
    expect(container.textContent).toContain("150,000");
    expect(container.textContent).toContain("Create App");
    fireEvent.click(getByText("API Docs"));
    expect(onNav).toHaveBeenCalledWith("/docs/api");
  });
});
