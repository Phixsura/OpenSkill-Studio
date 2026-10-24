import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApprovalPolicyPanel } from "@/components/approval-policy-panel";
describe("ApprovalPolicyPanel", () => {
  it("renders approval needed", () => {
    const { container } = render(
      <ApprovalPolicyPanel requiresApproval={true} autoApprove={false}
        requiredApprovers={["team-lead", "sre"]}
        matchedPolicies={["prod_deploy"]} />
    );
    expect(container.textContent).toContain("Approval Policy");
    expect(container.textContent).toContain("2 approvers needed");
    expect(container.textContent).toContain("team-lead, sre");
    expect(container.textContent).toContain("prod_deploy");
  });
  it("renders auto-approved", () => {
    const { container } = render(
      <ApprovalPolicyPanel requiresApproval={false} autoApprove={true}
        requiredApprovers={[]} matchedPolicies={[]} />
    );
    expect(container.textContent).toContain("Auto-approved");
  });
});
