import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTlsMgrPanel } from "@/components/fleet-ai-tls-mgr-panel";
describe("FleetAiTlsMgrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTlsMgrPanel managers={3} active={3} certs={1000} expiring={0} autoRenewed={200} />);
    expect(container.textContent).toContain("TLS Manager");
}); });
