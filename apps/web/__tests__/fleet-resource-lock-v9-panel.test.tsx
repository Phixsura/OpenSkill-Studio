import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetResourceLockV9Panel } from "@/components/fleet-resource-lock-v9-panel";
describe("FleetResourceLockV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetResourceLockV9Panel locks={50} contentions={3} />);
    expect(container.textContent).toContain("Resource Lock v9");
}); });
