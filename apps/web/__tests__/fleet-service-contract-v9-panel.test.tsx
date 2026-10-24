import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceContractV9Panel } from "@/components/fleet-service-contract-v9-panel";
describe("FleetServiceContractV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceContractV9Panel contracts={50} compliant={50} />);
    expect(container.textContent).toContain("Service Contract v9");
}); });
