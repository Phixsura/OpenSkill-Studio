import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatSecretV3Panel } from "@/components/fleet-ai-plat-secret-v3-panel";
describe("FleetAiPlatSecretV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatSecretV3Panel managers={3} active={3} secrets={10000} rotations={500} encrypted={true} />);
    expect(container.textContent).toContain("AI Secrets v3");
}); });
