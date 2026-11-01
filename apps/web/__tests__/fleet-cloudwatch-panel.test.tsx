import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudwatchPanel } from "@/components/fleet-cloudwatch-panel";
describe("FleetCloudwatchPanel", () => { it("renders", () => {
    const { container } = render(<FleetCloudwatchPanel total={200} ok={190} alarm={5} insufficient={5} />);
    expect(container.textContent).toContain("CloudWatch");
}); });
