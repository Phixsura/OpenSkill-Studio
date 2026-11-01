import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRetryPolPanel } from "@/components/fleet-ai-retry-pol-panel";
describe("FleetAiRetryPolPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRetryPolPanel policies={6} active={6} retries={100000} successRetries={96000} maxAttempts={5} />);
    expect(container.textContent).toContain("Retry Policy");
}); });
