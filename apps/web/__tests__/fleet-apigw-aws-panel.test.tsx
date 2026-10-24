import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApigwAwsPanel } from "@/components/fleet-apigw-aws-panel";
describe("FleetApigwAwsPanel", () => { it("renders", () => {
    const { container } = render(<FleetApigwAwsPanel apis={10} deployed={10} requests={50000000} throttled={200} />);
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("50,000,000");
}); });
