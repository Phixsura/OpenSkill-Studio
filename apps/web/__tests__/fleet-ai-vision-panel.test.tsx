import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiVisionPanel } from "@/components/fleet-ai-vision-panel";
describe("FleetAiVisionPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiVisionPanel services={5} active={5} images={10000000} detections={50000000} />);
    expect(container.textContent).toContain("AI Vision");
}); });
