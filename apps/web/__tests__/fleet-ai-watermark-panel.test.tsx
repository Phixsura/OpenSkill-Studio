import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWatermarkPanel } from "@/components/fleet-ai-watermark-panel";
describe("FleetAiWatermarkPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiWatermarkPanel systems={3} active={3} watermarked={5000000} detected={4750000} rate={95} />);
    expect(container.textContent).toContain("Watermark");
}); });
