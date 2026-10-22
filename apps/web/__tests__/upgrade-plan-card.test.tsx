import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UpgradePlanCard } from "@/components/upgrade-plan-card";

describe("UpgradePlanCard", () => {
  it("shows version", () => {
    const { container } = render(<UpgradePlanCard targetVersion="2.0" total={10} autoUpgrade={8} manualUpgrade={2} needsConsent={false} newPermissions={[]} />);
    expect(container.textContent).toContain("v2.0");
  });
  it("shows counts", () => {
    const { container } = render(<UpgradePlanCard targetVersion="2.0" total={10} autoUpgrade={7} manualUpgrade={3} needsConsent={false} newPermissions={[]} />);
    expect(container.textContent).toContain("7");
    expect(container.textContent).toContain("3");
  });
  it("shows new permissions", () => {
    const { container } = render(<UpgradePlanCard targetVersion="2.0" total={5} autoUpgrade={0} manualUpgrade={5} needsConsent={true} newPermissions={["write:cohorts"]} />);
    expect(container.textContent).toContain("write:cohorts");
  });
});
