import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatBakV2Panel } from "@/components/fleet-ai-plat-bak-v2-panel";
describe("FleetAiPlatBakV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatBakV2Panel systems={3} active={3} backups={144} sizeTb={5000} rpo={3} verified={true} />);
    expect(container.textContent).toContain("Backup v2");
}); });
