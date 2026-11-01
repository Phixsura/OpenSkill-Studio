import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMultimodalPanel } from "@/components/fleet-ai-multimodal-panel";
describe("FleetAiMultimodalPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiMultimodalPanel pipelines={6} active={6} modalities={["text", "image", "audio", "video"]} requests={5000000} />);
    expect(container.textContent).toContain("Multimodal");
}); });
