import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PortalFooter } from "@/components/portal-footer";

const LINKS = { Platform: [{ label: "Marketplace", url: "/marketplace" }], SDKs: [{ label: "TypeScript", url: "/ts" }] };

describe("PortalFooter", () => {
  it("shows sections", () => {
    const { container } = render(<PortalFooter links={LINKS} version="1.0.0" copyright="© 2026" />);
    expect(container.textContent).toContain("Platform");
    expect(container.textContent).toContain("SDKs");
  });
  it("shows version", () => {
    const { container } = render(<PortalFooter links={LINKS} version="1.0.0" copyright="© 2026" />);
    expect(container.textContent).toContain("v1.0.0");
    expect(container.textContent).toContain("© 2026");
  });
});
