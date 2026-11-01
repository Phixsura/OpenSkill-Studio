import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCanaryDepPanel } from "@/components/fleet-ai-canary-dep-panel";
describe("FleetAiCanaryDepPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCanaryDepPanel deploys={8} active={8} canaryPct={15} rollbacks={0} promotions={12} />);
    expect(container.textContent).toContain("Canary Deploy");
}); });
