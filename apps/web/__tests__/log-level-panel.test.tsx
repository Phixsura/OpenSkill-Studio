import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LogLevelPanel } from "@/components/log-level-panel";

describe("LogLevelPanel", () => {
  it("renders", () => {
    const { container } = render(
      <LogLevelPanel defaultLevel="info" overriddenCount={1}
        services={[
          { service: "api", level: "debug", overridden: true },
          { service: "worker", level: "info", overridden: false },
        ]} />
    );
    expect(container.textContent).toContain("Log Levels");
    expect(container.textContent).toContain("default: info");
    expect(container.textContent).toContain("1 overrides");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("debug");
    expect(container.textContent).toContain("override");
  });
});
