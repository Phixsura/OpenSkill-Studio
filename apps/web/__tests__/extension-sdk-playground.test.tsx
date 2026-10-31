import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionSDKPlayground } from "@/components/extension-sdk-playground";

const mockMethods = [
  {
    name: "getExtension", description: "Get extension details", category: "Extensions",
    params: [{ name: "extensionId", type: "string", required: true }],
    returnType: "Extension", example: 'sdk.getExtension("ext-1")',
  },
  {
    name: "listWebhooks", description: "List webhook subscriptions", category: "Webhooks",
    params: [], returnType: "Webhook[]", example: "sdk.listWebhooks()",
  },
  {
    name: "emitEvent", description: "Emit a custom event", category: "Events",
    params: [
      { name: "type", type: "string", required: true },
      { name: "payload", type: "object", required: false },
    ],
    returnType: "void", example: 'sdk.emitEvent("user.action", {})',
  },
];

describe("ExtensionSDKPlayground", () => {
  it("renders methods grouped by category", () => {
    const { container } = render(<ExtensionSDKPlayground methods={mockMethods} />);
    expect(container.textContent).toContain("SDK Playground");
    expect(container.textContent).toContain("Extensions");
    expect(container.textContent).toContain("Webhooks");
    expect(container.textContent).toContain("getExtension");
  });

  it("shows method details when selected", () => {
    const { container, getByText } = render(<ExtensionSDKPlayground methods={mockMethods} />);
    fireEvent.click(getByText("listWebhooks"));
    expect(container.textContent).toContain("List webhook subscriptions");
    expect(container.textContent).toContain("Webhook[]");
  });

  it("executes and shows output", () => {
    const onExecute = vi.fn();
    const { getByText } = render(
      <ExtensionSDKPlayground methods={mockMethods} onExecute={onExecute} />
    );
    fireEvent.click(getByText("▶ Execute"));
    expect(onExecute).toHaveBeenCalledWith("getExtension", {});
  });
});
