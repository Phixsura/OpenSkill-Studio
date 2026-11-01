import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-service-dependency-health-card";

describe("ConsumerApiServiceDependencyHealthCard", () => {
  it("shows dependencies", () => {
    const deps = [{ id: "db", name: "Database", status: "healthy", criticality: "required", responseMs: 5 }];
    const { container } = render(<Card overall="healthy" dependencies={deps} healthy={1} degraded={0} down={0} appName="App" />);
    expect(container.textContent).toContain("Service Dependencies");
    expect(container.textContent).toContain("Database");
    expect(container.textContent).toContain("required");
    expect(container.textContent).toContain("5ms");
  });
  it("shows empty", () => {
    const { container } = render(<Card overall="healthy" dependencies={[]} healthy={0} degraded={0} down={0} appName="App" />);
    expect(container.textContent).toContain("No dependencies");
  });
});
