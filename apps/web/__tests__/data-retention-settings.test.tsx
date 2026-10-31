import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataRetentionSettings } from "@/components/data-retention-settings";

describe("DataRetentionSettings", () => {
  const policies = [
    { data_type: "api_logs", retention_days: 90, category: "operations", is_custom: false },
    { data_type: "audit_logs", retention_days: 730, category: "compliance", is_custom: true },
  ];
  it("renders", () => {
    const { container } = render(<DataRetentionSettings policies={policies} onUpdate={vi.fn()} />);
    expect(container.textContent).toContain("Data Retention");
    expect(container.textContent).toContain("api logs");
    expect(container.textContent).toContain("audit logs");
    expect(container.textContent).toContain("Custom");
    expect(container.querySelectorAll("select").length).toBe(2);
  });
});
