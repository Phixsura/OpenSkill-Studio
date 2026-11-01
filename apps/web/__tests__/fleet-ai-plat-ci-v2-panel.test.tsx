import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatCiV2Panel } from "@/components/fleet-ai-plat-ci-v2-panel";
describe("FleetAiPlatCiV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatCiV2Panel pipelines={5} active={5} builds={5000} passRate={99.5} duration={5} />);
    expect(container.textContent).toContain("AI CI v2");
}); });
