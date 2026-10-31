import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployApprovalCard } from "@/components/deploy-approval-card";

describe("DeployApprovalCard", () => {
  it("renders pending", () => {
    const { container } = render(
      <DeployApprovalCard deployId="d1" version="2.0.0" env="prod"
        status="pending" approvals={1} required={2} />
    );
    expect(container.textContent).toContain("Deploy Approval");
    expect(container.textContent).toContain("pending");
    expect(container.textContent).toContain("d1");
    expect(container.textContent).toContain("2.0.0");
    expect(container.textContent).toContain("1/2");
  });
  it("renders rejected", () => {
    const { container } = render(
      <DeployApprovalCard deployId="d2" version="3.0.0" env="staging"
        status="rejected" approvals={0} required={2} rejectionReason="failing tests" />
    );
    expect(container.textContent).toContain("rejected");
    expect(container.textContent).toContain("failing tests");
  });
});
