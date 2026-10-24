import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBlueGreenV9Panel } from "@/components/fleet-blue-green-v9-panel";
describe("FleetBlueGreenV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetBlueGreenV9Panel activeEnv="blue" total={10} />);
    expect(container.textContent).toContain("Blue-Green v9");
}); });
