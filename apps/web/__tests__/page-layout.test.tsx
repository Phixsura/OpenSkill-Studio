import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PageLayout } from "@/components/page-layout";

describe("PageLayout", () => {
  it("renders layout", () => {
    const { container } = render(
      <PageLayout pageTitle="Settings" breadcrumbs={[{ label: "Home", href: "/" }, { label: "Settings", href: null }]}
        sidebar={[{ label: "General", href: "/settings", icon: "⚙️", active: true, badge: null }]}
        user={{ name: "Alice", initials: "AC" }} notifications={3} onNavigate={vi.fn()}>
        <p>Content here</p>
      </PageLayout>
    );
    expect(container.textContent).toContain("Home");
    expect(container.textContent).toContain("Settings");
    expect(container.textContent).toContain("General");
    expect(container.textContent).toContain("AC");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("Content here");
  });
});
