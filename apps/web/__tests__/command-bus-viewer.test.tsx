import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CommandBusViewer } from "@/components/command-bus-viewer";

describe("CommandBusViewer", () => {
  it("renders bus", () => {
    const { container } = render(
      <CommandBusViewer totalDispatched={10} registeredCommands={5}
        byCommand={{ "deploy.start": 5, "user.create": 3 }}
        history={[
          { command: "deploy.start", handler: "deploy_handler", status: "executed" },
          { command: "user.create", handler: "user_handler", status: "executed" },
        ]} />
    );
    expect(container.textContent).toContain("Command Bus");
    expect(container.textContent).toContain("5 commands");
    expect(container.textContent).toContain("10 dispatched");
    expect(container.textContent).toContain("deploy.start");
    expect(container.textContent).toContain("deploy_handler");
  });
});
