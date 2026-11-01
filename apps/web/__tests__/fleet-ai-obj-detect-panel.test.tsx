import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiObjDetectPanel } from "@/components/fleet-ai-obj-detect-panel";
describe("FleetAiObjDetectPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiObjDetectPanel detectors={6} active={6} frames={200000000} objects={2000000000} mapScore={95} />);
    expect(container.textContent).toContain("Object Detection");
}); });
