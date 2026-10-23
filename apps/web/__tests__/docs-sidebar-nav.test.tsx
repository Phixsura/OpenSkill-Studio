import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DocsSidebarNav } from "@/components/docs-sidebar-nav";

describe("DocsSidebarNav", () => {
  it("renders nav", () => {
    const onNav = vi.fn();
    const { container, getByText } = render(
      <DocsSidebarNav activeSlug="authentication" onNavigate={onNav} sections={[
        { slug: "api-reference", title: "API Reference", children: [
          { slug: "authentication", title: "Authentication" },
          { slug: "apps", title: "Apps API" },
        ]},
      ]} />
    );
    expect(container.textContent).toContain("API Reference");
    expect(container.textContent).toContain("Authentication");
    expect(container.textContent).toContain("Apps API");
    fireEvent.click(getByText("Apps API"));
    expect(onNav).toHaveBeenCalledWith("apps");
  });
});
