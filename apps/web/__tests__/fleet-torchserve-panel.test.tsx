import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTorchservePanel } from "@/components/fleet-torchserve-panel";
describe("FleetTorchservePanel", () => { it("renders", () => {
    const { container } = render(<FleetTorchservePanel instances={5} healthy={5} models={20} predictions={5000000} />);
    expect(container.textContent).toContain("TorchServe");
}); });
