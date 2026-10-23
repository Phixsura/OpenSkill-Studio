import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeployApprovalCard } from "@/components/deploy-approval-card";

describe("DeployApprovalCard", () => {
  it("renders approval", () => {
    const { container } = render(
      <DeployApprovalCard deployId="d1" environment="production" requester="alice"
        requiredApprovers={["bob", "carol"]} approvals={[{ approver: "bob" }]}
        status="pending" onApprove={vi.fn()} onReject={vi.fn()} />
    );
    expect(container.textContent).toContain("Deploy Approval");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("bob");
    expect(container.textContent).toContain("carol");
    expect(container.textContent).toContain("Approve");
    expect(container.textContent).toContain("Reject");
  });
});
