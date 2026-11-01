import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudWafV9Panel } from "@/components/fleet-cloud-waf-v9-panel";
describe("FleetCloudWafV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCloudWafV9Panel rules={100} blocked={10000} />);
    expect(container.textContent).toContain("Cloud WAF v9");
}); });
