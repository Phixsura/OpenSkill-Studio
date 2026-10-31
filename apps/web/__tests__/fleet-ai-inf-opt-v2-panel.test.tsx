import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiInfOptV2Panel } from "@/components/fleet-ai-inf-opt-v2-panel";
describe("FleetAiInfOptV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiInfOptV2Panel optimizers={4} active={4} models={200} speedup={5} techniques={8} />);
    expect(container.textContent).toContain("Inference Optimizer v2");
}); });
