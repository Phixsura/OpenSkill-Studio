import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployWindowViewer } from "@/components/deploy-window-viewer";

describe("DeployWindowViewer", () => {
  it("renders", () => {
    const { container } = render(
      <DeployWindowViewer currentlyInWindow={false} nextWindowHours={40}
        windows={[
          { name: "maintenance", dayOfWeek: 6, startHour: 2, durationHours: 4 },
          { name: "deploy", dayOfWeek: 3, startHour: 14, durationHours: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Deploy Windows");
    expect(container.textContent).toContain("Next in 40h");
    expect(container.textContent).toContain("maintenance");
    expect(container.textContent).toContain("Sat");
    expect(container.textContent).toContain("2:00");
    expect(container.textContent).toContain("4h");
  });
});
