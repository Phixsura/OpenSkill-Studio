import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CompletePageLayout } from "@/components/complete-page-layout";

describe("CompletePageLayout", () => {
  it("renders page", () => {
    const onNav = vi.fn();
    const { container, getByText } = render(
      <CompletePageLayout title="App Settings" hasSidebar={true} onNavigate={onNav}
        breadcrumbs={[{ label: "Home", path: "/" }, { label: "Settings", path: "/settings" }]}
        sections={[
          { id: "general", title: "General", type: "form", collapsed: false },
          { id: "danger", title: "Danger Zone", type: "danger", collapsed: true },
        ]}>
        <p>Page content</p>
      </CompletePageLayout>
    );
    expect(container.textContent).toContain("App Settings");
    expect(container.textContent).toContain("Home");
    expect(container.textContent).toContain("General");
    expect(container.textContent).toContain("Danger Zone");
    expect(container.textContent).toContain("Page content");
    fireEvent.click(getByText("Home"));
    expect(onNav).toHaveBeenCalledWith("/");
  });
});
