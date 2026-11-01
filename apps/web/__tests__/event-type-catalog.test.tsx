import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventTypeCatalog } from "@/components/event-type-catalog";

describe("EventTypeCatalog", () => {
  const events = [
    { id: "app.installed", description: "App installed", category: "Apps", fields: ["app_id"], fieldCount: 1 },
    { id: "deploy.started", description: "Deploy started", category: "Deployments", fields: ["deploy_id"], fieldCount: 1 },
  ];
  it("renders events", () => {
    const { container } = render(<EventTypeCatalog events={events} categories={["Apps", "Deployments"]} />);
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("deploy.started");
    expect(container.textContent).toContain("2 events");
  });
  it("filters", () => {
    const { container } = render(<EventTypeCatalog events={events} categories={["Apps", "Deployments"]} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Apps")!);
    expect(container.textContent).toContain("1 events");
  });
});
