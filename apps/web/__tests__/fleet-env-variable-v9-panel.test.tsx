import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEnvVariableV9Panel } from "@/components/fleet-env-variable-v9-panel";
describe("FleetEnvVariableV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetEnvVariableV9Panel total={200} encrypted={200} />);
    expect(container.textContent).toContain("Env Variables v9");
}); });
