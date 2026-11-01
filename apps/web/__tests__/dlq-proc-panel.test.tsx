import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DlqProcPanel } from "@/components/dlq-proc-panel";
describe("DlqProcPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DlqProcPanel reprocessed={5} discarded={2}
        messages={[
          { id: "m1", error: "timeout", attempts: 3 },
          { id: "m2", error: "500 error", attempts: 5 },
        ]} />
    );
    expect(container.textContent).toContain("Dead Letter Queue");
    expect(container.textContent).toContain("2 pending");
    expect(container.textContent).toContain("5 retried");
    expect(container.textContent).toContain("m1");
    expect(container.textContent).toContain("timeout");
  });
});
