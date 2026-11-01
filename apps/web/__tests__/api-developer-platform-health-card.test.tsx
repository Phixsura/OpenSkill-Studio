import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformHealthCard from "../src/components/api-developer-platform-health-card";

const health = { api_health: 98, webhook_health: 97, documentation_health: 96, developer_experience: 95, overall: 96.5, grade: "A+" };

describe("APIDeveloperPlatformHealthCard", () => {
  it("shows health with grade", () => {
    const { container } = render(<APIDeveloperPlatformHealthCard health={health} appName="App" />);
    expect(container.textContent).toContain("Platform Health");
    expect(container.textContent).toContain("A+");
    expect(container.textContent).toContain("96.5%");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("98%");
    expect(container.textContent).toContain("Dev Experience");
  });
});
