import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRuntimeProtectionV9Panel } from "@/components/fleet-runtime-protection-v9-panel";
describe("FleetRuntimeProtectionV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetRuntimeProtectionV9Panel agents={20} blocked={50} />);
    expect(container.textContent).toContain("Runtime Protection v9");
}); });
