import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMultimodalPanel } from "@/components/fleet-ai-multimodal-panel";
describe("FleetAiMultimodalPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiMultimodalPanel services={5} active={5} imageCalls={2000000} audioCalls={500000} videoCalls={200000} totalCalls={2700000} />);
    expect(container.textContent).toContain("AI Multimodal");
}); });
