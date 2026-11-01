import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApprovalChainPanel } from "@/components/approval-chain-panel";
describe("ApprovalChainPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ApprovalChainPanel deployId="d1" status="pending" currentLevel={1}
        levels={[
          { approver: "lead", role: "team_lead", approved: true },
          { approver: "sre", role: "sre", approved: false },
          { approver: "vp", role: "executive", approved: false },
        ]} />
    );
    expect(container.textContent).toContain("Approval Chain: d1");
    expect(container.textContent).toContain("Level 2/3");
    expect(container.textContent).toContain("lead (team_lead)");
    expect(container.textContent).toContain("sre (sre)");
    expect(container.textContent).toContain("vp (executive)");
  });
});
