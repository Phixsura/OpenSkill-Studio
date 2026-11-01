import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OpsReadyPanel } from "@/components/ops-ready-panel";
describe("OpsReadyPanel", () => {
  it("renders ready", () => {
    const { container } = render(
      <OpsReadyPanel ready={true} score={100} met={3} total={3} blocking={[]}
        requirements={[
          { name: "monitoring", category: "obs", met: true, severity: "required" },
          { name: "runbooks", category: "ops", met: true, severity: "required" },
          { name: "load_tests", category: "test", met: true, severity: "recommended" },
        ]} />
    );
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("OPERATIONALLY READY");
    expect(container.textContent).toContain("3/3");
    expect(container.textContent).toContain("monitoring");
  });
  it("renders not ready", () => {
    const { container } = render(
      <OpsReadyPanel ready={false} score={50} met={1} total={2} blocking={["monitoring"]}
        requirements={[
          { name: "monitoring", category: "obs", met: false, severity: "required" },
          { name: "alerts", category: "obs", met: true, severity: "required" },
        ]} />
    );
    expect(container.textContent).toContain("NOT READY");
    expect(container.textContent).toContain("Blocking: monitoring");
  });
});
