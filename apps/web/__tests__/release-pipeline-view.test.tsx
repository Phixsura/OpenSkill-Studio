import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleasePipelineView } from "@/components/release-pipeline-view";

describe("ReleasePipelineView", () => {
  it("renders stages", () => {
    const stages = [
      { name: "Tests", status: "passed", gate_type: "test_pass" },
      { name: "Security", status: "running", gate_type: "security_scan" },
      { name: "Deploy", status: "pending", gate_type: "manual_approval" },
    ];
    const { container } = render(<ReleasePipelineView stages={stages} status="in_progress" progressPct={33} />);
    expect(container.textContent).toContain("Tests");
    expect(container.textContent).toContain("Security");
    expect(container.textContent).toContain("in_progress");
  });
  it("shows blocked", () => {
    const stages = [{ name: "Tests", status: "failed", gate_type: "test_pass", reason: "3 tests failed" }];
    const { container } = render(<ReleasePipelineView stages={stages} status="blocked" progressPct={0} />);
    expect(container.textContent).toContain("blocked");
    expect(container.textContent).toContain("3 tests failed");
  });
});
