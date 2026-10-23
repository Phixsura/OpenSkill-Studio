import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangeRequestCard } from "@/components/change-request-card";

describe("ChangeRequestCard", () => {
  it("renders", () => {
    const { container } = render(
      <ChangeRequestCard crId="CR-ABC1" title="Deploy v3" description="Major version"
        risk="high" requester="alice" currentApprovals={1} minApprovals={2}
        status="pending" onApprove={vi.fn()} onReject={vi.fn()} />
    );
    expect(container.textContent).toContain("CR-ABC1");
    expect(container.textContent).toContain("Deploy v3");
    expect(container.textContent).toContain("high");
    expect(container.textContent).toContain("1/2");
    expect(container.textContent).toContain("Approve");
  });
  it("approve", () => {
    const fn = vi.fn();
    const { container } = render(
      <ChangeRequestCard crId="CR-1" title="X" description="Y" risk="low"
        requester="a" currentApprovals={0} minApprovals={1} status="pending"
        onApprove={fn} onReject={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Approve")!);
    expect(fn).toHaveBeenCalled();
  });
});
