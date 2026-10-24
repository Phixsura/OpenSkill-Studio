import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqLifecyclePanel } from "@/components/req-lifecycle-panel";
describe("ReqLifecyclePanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReqLifecyclePanel requestId="req-1" totalMs={60} success={true}
        stages={[
          { stage: "auth", durationMs: 5, status: "ok" },
          { stage: "process", durationMs: 50, status: "ok" },
          { stage: "serialize", durationMs: 5, status: "ok" },
        ]} />
    );
    expect(container.textContent).toContain("Request Lifecycle");
    expect(container.textContent).toContain("req-1");
    expect(container.textContent).toContain("60ms");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("process");
  });
});
