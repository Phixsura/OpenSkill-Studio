import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SecretAuditReport } from "@/components/secret-audit-report";

describe("SecretAuditReport", () => {
  it("renders audit", () => {
    const { container } = render(
      <SecretAuditReport total={3} compliant={2} compliancePct={67} maxAgeDays={90}
        results={[
          { name: "DB_PASSWORD", ageDays: 95, daysUntilRotation: 0, status: "overdue" },
          { name: "API_KEY", ageDays: 50, daysUntilRotation: 40, status: "ok" },
        ]} />
    );
    expect(container.textContent).toContain("Secret Rotation Audit");
    expect(container.textContent).toContain("67% compliant");
    expect(container.textContent).toContain("DB_PASSWORD");
    expect(container.textContent).toContain("overdue");
    expect(container.textContent).toContain("95d old");
  });
});
