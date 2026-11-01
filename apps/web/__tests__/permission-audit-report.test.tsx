import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PermissionAuditReport } from "@/components/permission-audit-report";

describe("PermissionAuditReport", () => {
  it("renders clean audit", () => {
    const result = {
      extensionId: "ext-1", totalPermissions: 2, usedPermissions: 2,
      unusedPermissions: [], dangerousCombos: [], riskScore: 3,
      escalations: [], recommendation: "✅ Good: follows least-privilege principle",
    };
    const { container } = render(<PermissionAuditReport result={result} />);
    expect(container.textContent).toContain("2/2 used (100%)");
    expect(container.textContent).toContain("least-privilege");
    expect(container.textContent).toContain("Risk Score: 3");
  });

  it("renders dangerous audit with escalations", () => {
    const result = {
      extensionId: "ext-1", totalPermissions: 4, usedPermissions: 1,
      unusedPermissions: ["write:data (never used)", "admin:settings (stale)"],
      dangerousCombos: ["Code execution + outbound webhooks = exfiltration risk"],
      riskScore: 18, escalations: ["2.0.0: added admin:settings (risk 5/5)"],
      recommendation: "🔴 Review 1 dangerous combination(s)",
    };
    const { container } = render(<PermissionAuditReport result={result} />);
    expect(container.textContent).toContain("1/4 used (25%)");
    expect(container.textContent).toContain("exfiltration risk");
    expect(container.textContent).toContain("admin:settings");
    expect(container.textContent).toContain("Risk Score: 18");
  });
});
