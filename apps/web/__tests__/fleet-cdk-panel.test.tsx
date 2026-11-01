import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCdkPanel } from "@/components/fleet-cdk-panel";
describe("FleetCdkPanel", () => { it("renders", () => {
    const { container } = render(<FleetCdkPanel total={15} deployed={14} failed={0} drifted={1} />);
    expect(container.textContent).toContain("AWS CDK");
    expect(container.textContent).toContain("1 drifted");
}); });
