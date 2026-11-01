import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatSvlessV2Panel } from "@/components/fleet-ai-plat-svless-v2-panel";
describe("FleetAiPlatSvlessV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatSvlessV2Panel platforms={4} active={4} functions={2000} invocations={500000000} coldMs={80} />);
    expect(container.textContent).toContain("Serverless v2");
}); });
