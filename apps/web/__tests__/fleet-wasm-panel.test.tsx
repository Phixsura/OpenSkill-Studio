import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWasmPanel } from "@/components/fleet-wasm-panel";
describe("FleetWasmPanel", () => { it("renders", () => {
    const { container } = render(<FleetWasmPanel modules={20} loaded={20} executions={5000000} avgExec={3} />);
    expect(container.textContent).toContain("WASM");
    expect(container.textContent).toContain("5,000,000");
}); });
