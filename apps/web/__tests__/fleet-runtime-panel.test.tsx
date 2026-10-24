import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRuntimePanel } from "@/components/fleet-runtime-panel";
describe("FleetRuntimePanel", () => { it("renders", () => {
    const { container } = render(<FleetRuntimePanel total={10} heterogeneous={true} />);
    expect(container.textContent).toContain("Container Runtime");
    expect(container.textContent).toContain("Mixed runtimes");
}); });
