import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOnnxPanel } from "@/components/fleet-onnx-panel";
describe("FleetOnnxPanel", () => { it("renders", () => {
    const { container } = render(<FleetOnnxPanel instances={5} running={5} models={30} infPerSec={500000} />);
    expect(container.textContent).toContain("ONNX");
}); });
