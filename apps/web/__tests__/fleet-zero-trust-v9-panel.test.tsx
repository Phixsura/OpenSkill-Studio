import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetZeroTrustV9Panel } from "@/components/fleet-zero-trust-v9-panel";
describe("FleetZeroTrustV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetZeroTrustV9Panel policies={20} sessions={5000} />);
    expect(container.textContent).toContain("Zero Trust v9");
}); });
