import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtensionMessageLog } from "@/components/extension-message-log";

const MSGS = [
  { type: "ready", direction: "in" as const, timestamp: "10:00:01" },
  { type: "context", direction: "out" as const, timestamp: "10:00:02" },
];

describe("ExtensionMessageLog", () => {
  it("shows messages", () => {
    const { container } = render(<ExtensionMessageLog messages={MSGS} />);
    expect(container.textContent).toContain("ready");
    expect(container.textContent).toContain("context");
  });
  it("empty state", () => {
    const { container } = render(<ExtensionMessageLog messages={[]} />);
    expect(container.textContent).toContain("No messages");
  });
});
