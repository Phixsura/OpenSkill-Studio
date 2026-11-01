import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudNativeV9Panel } from "@/components/fleet-cloud-native-v9-panel";
describe("FleetCloudNativeV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCloudNativeV9Panel workloads={100} maturity={4.5} />);
    expect(container.textContent).toContain("Cloud Native v9");
}); });
