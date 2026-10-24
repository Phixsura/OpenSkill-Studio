import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Footer } from "@/components/footer";

describe("Footer", () => {
  const sections = {
    Product: [{ label: "Features", href: "/features" }],
    Legal: [{ label: "Privacy", href: "/privacy" }],
  };
  it("renders footer", () => {
    const { container } = render(<Footer sections={sections} copyright="© 2026 OpenSkill" />);
    expect(container.textContent).toContain("Product");
    expect(container.textContent).toContain("Features");
    expect(container.textContent).toContain("Privacy");
    expect(container.textContent).toContain("© 2026 OpenSkill");
  });
});
