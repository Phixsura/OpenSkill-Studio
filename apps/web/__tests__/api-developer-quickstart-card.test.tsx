import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperQuickstartCard from "../src/components/api-developer-quickstart-card";

const steps = [
  { step_id: "s1", title: "Install SDK", completed: true },
  { step_id: "s2", title: "Auth Setup", completed: false },
];

describe("APIDeveloperQuickstartCard", () => {
  it("shows progress", () => {
    const { container } = render(<APIDeveloperQuickstartCard language="JavaScript" steps={steps} completionPct={50} appName="App" />);
    expect(container.textContent).toContain("Quickstart");
    expect(container.textContent).toContain("JavaScript");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Install SDK");
  });
});
