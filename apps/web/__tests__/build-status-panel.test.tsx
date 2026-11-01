import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BuildStatusPanel } from "@/components/build-status-panel";

describe("BuildStatusPanel", () => {
  it("renders builds", () => {
    const { container } = render(
      <BuildStatusPanel total={100} passed={95} failed={5} running={2}
        passRate={95} avgDurationSec={180} health="green" />
    );
    expect(container.textContent).toContain("Build Status");
    expect(container.textContent).toContain("95% pass rate");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("180s");
  });
});
