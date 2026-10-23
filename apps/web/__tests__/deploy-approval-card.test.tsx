import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeployApprovalCard } from "@/components/deploy-approval-card";

describe("DeployApprovalCard", () => {
  it("renders pending approval", () => {
    const onApprove = vi.fn();
    const { container, getByText } = render(
      <DeployApprovalCard deployId="d1" version="2.0" env="production"
        requester="alice" status="pending" required={2}
        approvals={[{ approver: "bob", comment: "LGTM" }]}
        onApprove={onApprove} onReject={vi.fn()} />
    );
    expect(container.textContent).toContain("Deploy Approval");
    expect(container.textContent).toContain("pending");
    expect(container.textContent).toContain("2.0");
    expect(container.textContent).toContain("1/2");
    expect(container.textContent).toContain("bob");
    expect(container.textContent).toContain("LGTM");
    fireEvent.click(getByText("Approve"));
    expect(onApprove).toHaveBeenCalled();
  });
});
