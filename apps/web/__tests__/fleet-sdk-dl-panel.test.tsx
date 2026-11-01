import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSdkDlPanel } from "@/components/fleet-sdk-dl-panel";
describe("FleetSdkDlPanel", () => { it("renders", () => {
    const { container } = render(<FleetSdkDlPanel totalDownloads={130000} sdks={5} topSdk="TypeScript" topDownloads={80000} />);
    expect(container.textContent).toContain("SDK Downloads");
    expect(container.textContent).toContain("TypeScript");
}); });
