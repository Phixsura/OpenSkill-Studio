import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCfgValidatePanel } from "@/components/fleet-cfg-validate-panel";
describe("FleetCfgValidatePanel", () => { it("renders", () => {
    const { container } = render(<FleetCfgValidatePanel total={30} valid={28} invalid={2} safeToDeploy={false} />);
    expect(container.textContent).toContain("Config Validation");
    expect(container.textContent).toContain("2 invalid");
}); });
