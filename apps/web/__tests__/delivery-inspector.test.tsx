import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeliveryInspector } from "@/components/delivery-inspector";

describe("DeliveryInspector", () => {
  it("shows event type", () => {
    const { container } = render(<DeliveryInspector eventType="app.installed" url="u" status="delivered"
      httpStatus={200} durationMs={150} attempt={1} maxAttempts={5} error={null} timeline={[]} />);
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("200");
  });
  it("shows error", () => {
    const { container } = render(<DeliveryInspector eventType="x" url="u" status="failed"
      httpStatus={null} durationMs={null} attempt={3} maxAttempts={5} error="timeout" timeline={[]} />);
    expect(container.textContent).toContain("timeout");
  });
});
