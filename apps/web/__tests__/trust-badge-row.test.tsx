import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrustBadgeRow } from "@/components/trust-badge-row";

describe("TrustBadgeRow", () => {
  it("renders badges", () => {
    const { container } = render(
      <TrustBadgeRow trustLevel="high" trustScore={75} badges={[
        { id: "verified", icon: "✅", label: "Verified", color: "blue" },
        { id: "security_reviewed", icon: "🔒", label: "Security Reviewed", color: "green" },
      ]} />
    );
    expect(container.textContent).toContain("Verified");
    expect(container.textContent).toContain("Security Reviewed");
    expect(container.textContent).toContain("Trust: 75%");
  });
});
