import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRetryPolicyV9Panel } from "@/components/fleet-retry-policy-v9-panel";
describe("FleetRetryPolicyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetRetryPolicyV9Panel policies={20} retries={100} />);
    expect(container.textContent).toContain("Retry Policy v9");
}); });
