import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSemkernelPanel } from "@/components/fleet-semkernel-panel";
describe("FleetSemkernelPanel", () => { it("renders", () => {
    const { container } = render(<FleetSemkernelPanel apps={5} active={5} plugins={50} invocations={500000} />);
    expect(container.textContent).toContain("Semantic Kernel");
}); });
