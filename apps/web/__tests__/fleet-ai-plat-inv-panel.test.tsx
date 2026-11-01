import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatInvPanel } from "@/components/fleet-ai-plat-inv-panel";
describe("FleetAiPlatInvPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatInvPanel inventories={2} active={2} assets={50000} gpus={20000} storage={200} />);
    expect(container.textContent).toContain("Platform Inventory");
}); });
