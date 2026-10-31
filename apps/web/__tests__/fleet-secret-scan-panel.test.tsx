import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSecretScanPanel } from "@/components/fleet-secret-scan-panel";
describe("FleetSecretScanPanel", () => { it("renders", () => {
    const { container } = render(<FleetSecretScanPanel totalRepos={20} clean={18} leaked={5} allClean={false} />);
    expect(container.textContent).toContain("Secret Scanning");
    expect(container.textContent).toContain("5 secrets found");
}); });
