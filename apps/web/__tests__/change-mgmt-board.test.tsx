import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangeMgmtBoard } from "@/components/change-mgmt-board";

describe("ChangeMgmtBoard", () => {
  it("renders", () => {
    const { container } = render(
      <ChangeMgmtBoard byStatus={{ approved: 1, pending_review: 1 }}
        changes={[
          { id: "c1", title: "Update DNS", risk: "low", status: "approved", approvals: 1 },
          { id: "c2", title: "DB migration", risk: "high", status: "pending_review", approvals: 1 },
        ]} />
    );
    expect(container.textContent).toContain("Change Management");
    expect(container.textContent).toContain("2 changes");
    expect(container.textContent).toContain("Update DNS");
    expect(container.textContent).toContain("approved");
    expect(container.textContent).toContain("high");
    expect(container.textContent).toContain("pending_review");
  });
});
