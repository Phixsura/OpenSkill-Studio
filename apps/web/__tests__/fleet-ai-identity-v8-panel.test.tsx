import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiIdentityV8Panel } from "@/components/fleet-ai-identity-v8-panel";
describe("FleetAiIdentityV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiIdentityV8Panel providers={5} active={5} users={50000000} auth={2000000000} mfa={99.5} zt={true} />);
    expect(container.textContent).toContain("Identity v8");
}); });
