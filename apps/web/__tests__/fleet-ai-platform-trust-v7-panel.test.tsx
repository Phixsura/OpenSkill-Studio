import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatformTrustV7Panel } from "@/components/fleet-ai-platform-trust-v7-panel";
describe("FleetAiPlatformTrustV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatformTrustV7Panel systems={3} active={3} score={99} transparency={98} certs={["SOC2", "GDPR"]} />);
    expect(container.textContent).toContain("Platform Trust v7");
}); });
