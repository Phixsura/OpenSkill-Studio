import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiStorTierPanel } from "@/components/fleet-ai-stor-tier-panel";
describe("FleetAiStorTierPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiStorTierPanel tiers={3} active={3} hot={200} warm={1000} cold={10000} saved={65} />);
    expect(container.textContent).toContain("Storage Tiering");
}); });
