import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAdmissionPanel } from "@/components/fleet-admission-panel";
describe("FleetAdmissionPanel", () => { it("renders", () => {
    const { container } = render(<FleetAdmissionPanel webhooks={5} totalCalls={1500} denied={60} errors={2} healthy={false} />);
    expect(container.textContent).toContain("Admission Control");
    expect(container.textContent).toContain("Webhook errors");
}); });
