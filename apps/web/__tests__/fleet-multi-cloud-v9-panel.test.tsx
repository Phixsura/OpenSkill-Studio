import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMultiCloudV9Panel } from "@/components/fleet-multi-cloud-v9-panel";
describe("FleetMultiCloudV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetMultiCloudV9Panel providers={3} instances={350} />);
    expect(container.textContent).toContain("Multi-Cloud v9");
}); });
