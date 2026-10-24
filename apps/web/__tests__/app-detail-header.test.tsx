import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppDetailHeader } from "@/components/app-detail-header";

describe("AppDetailHeader", () => {
  it("renders", () => {
    const { container } = render(
      <AppDetailHeader name="Auth SDK" developer="Alice" tagline="Easy auth"
        iconLetter="A" rating={4.7} stars="★★★★★" reviewCount={120}
        installDisplay="8K+" priceLabel="Free" category="security"
        verified={true} version="2.1.0" onInstall={vi.fn()} />
    );
    expect(container.textContent).toContain("Auth SDK");
    expect(container.textContent).toContain("by Alice");
    expect(container.textContent).toContain("Easy auth");
    expect(container.textContent).toContain("★★★★★");
    expect(container.textContent).toContain("(120)");
    expect(container.textContent).toContain("8K+");
    expect(container.textContent).toContain("✓ Verified");
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("Install Free");
  });
});
