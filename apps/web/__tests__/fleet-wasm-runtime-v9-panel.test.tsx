import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWasmRuntimeV9Panel } from "@/components/fleet-wasm-runtime-v9-panel";
describe("FleetWasmRuntimeV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetWasmRuntimeV9Panel modules={20} invocations={100000} />);
    expect(container.textContent).toContain("WASM Runtime v9");
}); });
