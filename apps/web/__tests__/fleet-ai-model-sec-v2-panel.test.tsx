import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelSecV2Panel } from "@/components/fleet-ai-model-sec-v2-panel";
describe("FleetAiModelSecV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelSecV2Panel systems={3} active={3} models={1000} threats={200} encrypted={100} />);
    expect(container.textContent).toContain("Model Security v2");
}); });
