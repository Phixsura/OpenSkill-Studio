import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOnnxRtPanel } from "@/components/fleet-ai-onnx-rt-panel";
describe("FleetAiOnnxRtPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiOnnxRtPanel runtimes={5} active={5} models={200} inferences={500000000} speedup={4} />);
    expect(container.textContent).toContain("ONNX Runtime");
}); });
