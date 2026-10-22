import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CompatibilityBadge } from "@/components/compatibility-badge";

describe("CompatibilityBadge", () => {
  it("shows compatible", () => {
    const { container } = render(<CompatibilityBadge compatible={true} platformVersion="1.0.0" />);
    expect(container.textContent).toContain("Compatible");
    expect(container.textContent).toContain("✅");
  });
  it("shows incompatible", () => {
    const { container } = render(<CompatibilityBadge compatible={false} platformVersion="1.0.0" issues={2} />);
    expect(container.textContent).toContain("2 issues");
    expect(container.textContent).toContain("❌");
  });
  it("shows platform version", () => {
    const { container } = render(<CompatibilityBadge compatible={true} platformVersion="2.1.0" />);
    expect(container.textContent).toContain("v2.1.0");
  });
});
