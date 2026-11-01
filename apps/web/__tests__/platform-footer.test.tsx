import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformFooter } from "@/components/platform-footer";

describe("PlatformFooter", () => {
  it("renders footer", () => {
    const { container } = render(
      <PlatformFooter copyright="© 2026 OpenSkill" sections={[
        { title: "Product", links: [{ label: "Features", url: "/features" }, { label: "Pricing", url: "/pricing" }] },
        { title: "Legal", links: [{ label: "Privacy", url: "/privacy" }] },
      ]} />
    );
    expect(container.textContent).toContain("Product");
    expect(container.textContent).toContain("Features");
    expect(container.textContent).toContain("Pricing");
    expect(container.textContent).toContain("Legal");
    expect(container.textContent).toContain("Privacy");
    expect(container.textContent).toContain("© 2026 OpenSkill");
  });
});
