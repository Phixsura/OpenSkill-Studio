import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWhRetryPanel } from "@/components/fleet-wh-retry-panel";
describe("FleetWhRetryPanel", () => { it("renders", () => {
    const { container } = render(<FleetWhRetryPanel totalRetries={100} recovered={80} exhausted={20} recoveryRate={80} />);
    expect(container.textContent).toContain("Webhook Retries");
    expect(container.textContent).toContain("80% recovered");
}); });
