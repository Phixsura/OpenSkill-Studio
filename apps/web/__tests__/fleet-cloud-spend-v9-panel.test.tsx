import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudSpendV9Panel } from "@/components/fleet-cloud-spend-v9-panel";
describe("FleetCloudSpendV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCloudSpendV9Panel providers={3} daily={3000} />);
    expect(container.textContent).toContain("Cloud Spend v9");
}); });
