import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSecretScanPanel } from "@/components/fleet-ai-secret-scan-panel";
describe("FleetAiSecretScanPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSecretScanPanel scanners={3} active={3} repos={1000} found={20} revoked={20} />);
    expect(container.textContent).toContain("Secret Scanner");
}); });
