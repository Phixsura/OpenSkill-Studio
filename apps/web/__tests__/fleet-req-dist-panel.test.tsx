import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetReqDistPanel } from "@/components/fleet-req-dist-panel";
describe("FleetReqDistPanel", () => { it("renders", () => {
    const { container } = render(<FleetReqDistPanel totalRequests={10000} regions={3} hotspot="us-east" />);
    expect(container.textContent).toContain("Request Distribution");
    expect(container.textContent).toContain("us-east");
}); });
