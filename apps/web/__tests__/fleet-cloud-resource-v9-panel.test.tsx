import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudResourceV9Panel } from "@/components/fleet-cloud-resource-v9-panel";
describe("FleetCloudResourceV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCloudResourceV9Panel resources={500} waste={5} />);
    expect(container.textContent).toContain("Cloud Resource v9");
}); });
