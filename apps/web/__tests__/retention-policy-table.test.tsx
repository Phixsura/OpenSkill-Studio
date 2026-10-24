import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RetentionPolicyTable } from "@/components/retention-policy-table";

describe("RetentionPolicyTable", () => {
  it("renders policies and violations", () => {
    const { container } = render(
      <RetentionPolicyTable allCompliant={false}
        policies={[{ resource: "logs", retentionDays: 90, action: "delete", archive: false }]}
        violations={[{ resource: "logs", recordId: "l2", ageDays: 120, maxDays: 90, overdueDays: 30 }]} />
    );
    expect(container.textContent).toContain("Data Retention");
    expect(container.textContent).toContain("1 violations");
    expect(container.textContent).toContain("logs");
    expect(container.textContent).toContain("90d");
    expect(container.textContent).toContain("30d overdue");
  });
});
