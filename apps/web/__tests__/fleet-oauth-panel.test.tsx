import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOauthPanel } from "@/components/fleet-oauth-panel";
describe("FleetOauthPanel", () => { it("renders", () => {
    const { container } = render(<FleetOauthPanel issued={1000} active={750} revoked={50} revocationRate={5} />);
    expect(container.textContent).toContain("OAuth Tokens");
    expect(container.textContent).toContain("750 active");
}); });
