import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WarmupCtrlPanel } from "@/components/warmup-ctrl-panel";
describe("WarmupCtrlPanel", () => {
  it("renders", () => {
    const { container } = render(
      <WarmupCtrlPanel warm={1} cold={1}
        services={[
          { name: "api", status: "warm", steps: 3 },
          { name: "worker", status: "cold", steps: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Service Warmup");
    expect(container.textContent).toContain("1 warm");
    expect(container.textContent).toContain("1 cold");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("warm");
    expect(container.textContent).toContain("worker");
  });
});
