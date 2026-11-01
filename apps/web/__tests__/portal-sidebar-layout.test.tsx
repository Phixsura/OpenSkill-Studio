import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PortalSidebarLayout } from "@/components/portal-sidebar-layout";

describe("PortalSidebarLayout", () => {
  it("renders sidebar and content", () => {
    const { container } = render(<PortalSidebarLayout sidebar={<nav>Nav</nav>}><p>Content</p></PortalSidebarLayout>);
    expect(container.textContent).toContain("Nav");
    expect(container.textContent).toContain("Content");
  });
});
