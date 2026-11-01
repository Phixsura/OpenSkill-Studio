import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApprovalWorkflowCard } from "@/components/approval-workflow-card";

describe("ApprovalWorkflowCard", () => {
  it("renders pending", () => {
    const { container } = render(
      <ApprovalWorkflowCard type="publish" description="Publish v2" status="pending" requester="dev1" onApprove={vi.fn()} onReject={vi.fn()} />
    );
    expect(container.textContent).toContain("Publish v2");
    expect(container.textContent).toContain("pending");
    expect(container.textContent).toContain("Approve");
  });
  it("no buttons when approved", () => {
    const { container } = render(
      <ApprovalWorkflowCard type="publish" description="X" status="approved" requester="dev1" onApprove={vi.fn()} onReject={vi.fn()} />
    );
    expect(container.querySelectorAll("button").length).toBe(0);
  });
  it("calls onApprove", () => {
    const fn = vi.fn();
    const { container } = render(
      <ApprovalWorkflowCard type="publish" description="X" status="pending" requester="d" onApprove={fn} onReject={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Approve")!);
    expect(fn).toHaveBeenCalled();
  });
});
