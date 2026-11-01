import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRetryBoPanel } from "@/components/fleet-ai-retry-bo-panel";
describe("FleetAiRetryBoPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRetryBoPanel managers={4} active={4} retries={500000} maxBackoff={120} jitter={true} />);
    expect(container.textContent).toContain("Retry Backoff");
}); });
