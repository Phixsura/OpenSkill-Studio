import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRuntimeGuardV9Panel } from "@/components/fleet-runtime-guard-v9-panel";
describe("FleetRuntimeGuardV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetRuntimeGuardV9Panel guards={10} blocked={5} />);
    expect(container.textContent).toContain("Runtime Guard v9");
}); });
