import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployWindowSched } from "@/components/deploy-window-sched";

describe("DeployWindowSched", () => {
  it("renders", () => {
    const { container } = render(
      <DeployWindowSched currentWindow="business_hours" allowed={true} currentHour={14}
        windows={[
          { name: "business_hours", startHour: 9, endHour: 17 },
          { name: "off_peak", startHour: 22, endHour: 6 },
        ]} />
    );
    expect(container.textContent).toContain("Deploy Windows");
    expect(container.textContent).toContain("Deploy OK");
    expect(container.textContent).toContain("business hours");
    expect(container.textContent).toContain("9:00");
    expect(container.textContent).toContain("off peak");
  });
});
