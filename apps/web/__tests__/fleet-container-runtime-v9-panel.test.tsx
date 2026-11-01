import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetContainerRuntimeV9Panel } from "@/components/fleet-container-runtime-v9-panel";
describe("FleetContainerRuntimeV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetContainerRuntimeV9Panel containers={500} running={480} />);
    expect(container.textContent).toContain("Container Runtime v9");
}); });
