import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRuntimeConfigV9Panel } from "@/components/fleet-runtime-config-v9-panel";
describe("FleetRuntimeConfigV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetRuntimeConfigV9Panel configs={100} watchers={500} />);
    expect(container.textContent).toContain("Runtime Config v9");
}); });
