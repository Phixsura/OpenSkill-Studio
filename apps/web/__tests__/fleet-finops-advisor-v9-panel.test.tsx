import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFinopsAdvisorV9Panel } from "@/components/fleet-finops-advisor-v9-panel";
describe("FleetFinopsAdvisorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetFinopsAdvisorV9Panel total={30} savings={15000} />);
    expect(container.textContent).toContain("FinOps Advisor v9");
}); });
