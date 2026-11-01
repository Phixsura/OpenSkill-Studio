import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTensorrtPanel } from "@/components/fleet-tensorrt-panel";
describe("FleetTensorrtPanel", () => { it("renders", () => {
    const { container } = render(<FleetTensorrtPanel engines={10} active={10} throughput={1000000} p99={2} />);
    expect(container.textContent).toContain("TensorRT");
}); });
