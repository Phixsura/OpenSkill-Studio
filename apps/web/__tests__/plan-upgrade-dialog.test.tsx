import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlanUpgradeDialog } from "@/components/plan-upgrade-dialog";

describe("PlanUpgradeDialog", () => {
  it("renders upgrade", () => {
    const { container } = render(
      <PlanUpgradeDialog currentPlan="free" targetPlan="pro" isUpgrade={true}
        priceDiffDisplay="+$29/mo" newPrice={29} warning={null}
        onConfirm={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Upgrade");
    expect(container.textContent).toContain("$29/mo");
    expect(container.textContent).toContain("+$29/mo");
    expect(container.textContent).toContain("Upgrade Now");
  });
});
