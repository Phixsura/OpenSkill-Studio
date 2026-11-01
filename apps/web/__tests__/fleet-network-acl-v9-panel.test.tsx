import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNetworkAclV9Panel } from "@/components/fleet-network-acl-v9-panel";
describe("FleetNetworkAclV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetNetworkAclV9Panel acls={30} active={30} />);
    expect(container.textContent).toContain("Network ACL v9");
}); });
