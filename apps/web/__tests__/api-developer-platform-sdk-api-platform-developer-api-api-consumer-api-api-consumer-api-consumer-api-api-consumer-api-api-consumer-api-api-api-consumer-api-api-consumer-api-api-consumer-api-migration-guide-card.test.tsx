import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-api-consumer-api-api-consumer-api-api-consumer-api-migration-guide-card";

describe("MigrationGuideCard", () => {
  it("shows guide", () => {
    const steps = [{ id: "s1", title: "Update auth", breaking: true, completed: true }, { id: "s2", title: "Test", breaking: false, completed: false }];
    const { container } = render(<Card fromVersion="v1" toVersion="v2" title="Migration" steps={steps} progressPct={50} complete={false} breakingRemaining={0} appName="App" />);
    expect(container.textContent).toContain("Migration Guide");
    expect(container.textContent).toContain("v1 → v2");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Update auth");
  });
  it("shows breaking warning", () => {
    const { container } = render(<Card fromVersion="v1" toVersion="v2" title="M" steps={[]} progressPct={0} complete={false} breakingRemaining={2} appName="App" />);
    expect(container.textContent).toContain("2 breaking changes");
  });
});
