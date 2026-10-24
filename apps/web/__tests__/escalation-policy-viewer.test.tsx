import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EscalationPolicyViewer } from "@/components/escalation-policy-viewer";

describe("EscalationPolicyViewer", () => {
  it("renders policy", () => {
    const { container } = render(
      <EscalationPolicyViewer name="Critical Alerts"
        levels={[
          { level: 1, contacts: ["oncall"], channel: "pager", waitMin: 5 },
          { level: 2, contacts: ["manager"], channel: "phone", waitMin: 15 },
        ]}
        timeline={[
          { level: 1, atMin: 0, contacts: ["oncall"] },
          { level: 2, atMin: 5, contacts: ["manager"] },
        ]} />
    );
    expect(container.textContent).toContain("Critical Alerts");
    expect(container.textContent).toContain("2 levels");
    expect(container.textContent).toContain("oncall");
    expect(container.textContent).toContain("pager");
    expect(container.textContent).toContain("wait 5min");
    expect(container.textContent).toContain("L1 @0min");
  });
});
