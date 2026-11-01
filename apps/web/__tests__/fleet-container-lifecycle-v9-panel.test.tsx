import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetContainerLifecycleV9Panel } from "@/components/fleet-container-lifecycle-v9-panel";
describe("FleetContainerLifecycleV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetContainerLifecycleV9Panel containers={500} running={490} />);
    expect(container.textContent).toContain("Container Lifecycle v9");
}); });
