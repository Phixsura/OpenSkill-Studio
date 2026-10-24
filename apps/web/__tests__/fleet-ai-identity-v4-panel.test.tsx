import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiIdentityV4Panel } from "@/components/fleet-ai-identity-v4-panel";
describe("FleetAiIdentityV4Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiIdentityV4Panel providers={3} active={3} users={5000000} auth={200000000} mfa={99} zeroTrust={true} />);
    expect(container.textContent).toContain("Identity v4");
}); });
