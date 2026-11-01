import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PermissionRiskCard } from "@/components/permission-risk-card";

describe("PermissionRiskCard", () => {
  it("renders permissions", () => {
    const perms = [
      { scope: "read:users", label: "Read users", risk: "low", category: "users" },
      { scope: "admin:org", label: "Org admin", risk: "critical", category: "admin" },
    ];
    const { container } = render(<PermissionRiskCard permissions={perms} overallRisk="critical" requiresReview={true} />);
    expect(container.textContent).toContain("critical risk");
    expect(container.textContent).toContain("Read users");
    expect(container.textContent).toContain("admin review");
  });
  it("no review needed", () => {
    const { container } = render(
      <PermissionRiskCard permissions={[]} overallRisk="low" requiresReview={false} />
    );
    expect(container.textContent).not.toContain("admin review");
  });
});
