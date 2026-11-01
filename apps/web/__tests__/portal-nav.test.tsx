import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PortalNav } from "@/components/portal-nav";

describe("PortalNav", () => {
  it("shows all sections", () => {
    const { container } = render(<PortalNav activeSection="overview" />);
    expect(container.textContent).toContain("My Apps");
    expect(container.textContent).toContain("Documentation");
  });
  it("highlights active", () => {
    const { container } = render(<PortalNav activeSection="apps" />);
    const active = container.querySelector("[class*='blue']");
    expect(active?.textContent).toContain("My Apps");
  });
  it("renders 7 links", () => {
    const { container } = render(<PortalNav activeSection="" />);
    expect(container.querySelectorAll("a").length).toBe(7);
  });
});
