import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWatermarkPanel } from "@/components/fleet-ai-watermark-panel";
describe("FleetAiWatermarkPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiWatermarkPanel services={5} active={5} watermarked={5000000} verified={2500000} />);
    expect(container.textContent).toContain("AI Watermark");
}); });
