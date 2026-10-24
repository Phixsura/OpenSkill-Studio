import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCfnPanel } from "@/components/fleet-cfn-panel";
describe("FleetCfnPanel", () => { it("renders", () => {
    const { container } = render(<FleetCfnPanel total={30} complete={27} rollback={1} inProgress={2} />);
    expect(container.textContent).toContain("CloudFormation");
}); });
