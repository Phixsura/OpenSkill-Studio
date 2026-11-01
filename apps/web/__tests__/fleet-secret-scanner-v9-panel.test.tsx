import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSecretScannerV9Panel } from "@/components/fleet-secret-scanner-v9-panel";
describe("FleetSecretScannerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSecretScannerV9Panel repos={100} secretsFound={2} />);
    expect(container.textContent).toContain("Secret Scanner v9");
}); });
