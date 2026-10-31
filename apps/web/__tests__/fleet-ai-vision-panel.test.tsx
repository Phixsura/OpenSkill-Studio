import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiVisionPanel } from "@/components/fleet-ai-vision-panel";
describe("FleetAiVisionPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiVisionPanel pipelines={5} active={5} images={50000000} accuracy={98} models={8} />);
    expect(container.textContent).toContain("AI Vision");
}); });
