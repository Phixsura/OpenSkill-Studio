import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EsProjectorPanel } from "@/components/es-projector-panel";
describe("EsProjectorPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EsProjectorPanel totalEvents={5000}
        projections={[
          { name: "order_count", eventsApplied: 3000 },
          { name: "revenue", eventsApplied: 2000 },
        ]} />
    );
    expect(container.textContent).toContain("Event Projections");
    expect(container.textContent).toContain("5,000 events");
    expect(container.textContent).toContain("order_count");
    expect(container.textContent).toContain("3,000 events");
  });
});
