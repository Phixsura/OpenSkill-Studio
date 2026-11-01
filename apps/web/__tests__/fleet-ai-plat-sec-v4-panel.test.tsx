import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatSecV4Panel } from "@/components/fleet-ai-plat-sec-v4-panel";
describe("FleetAiPlatSecV4Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatSecV4Panel systems={5} active={5} score={99} threats={1000} zeroTrust={true} encrypted={100} />);
    expect(container.textContent).toContain("Security v4");
}); });
