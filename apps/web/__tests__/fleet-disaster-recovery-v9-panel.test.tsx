import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDisasterRecoveryV9Panel } from "@/components/fleet-disaster-recovery-v9-panel";
describe("FleetDisasterRecoveryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDisasterRecoveryV9Panel plans={5} tested={5} />);
    expect(container.textContent).toContain("Disaster Recovery v9");
}); });
