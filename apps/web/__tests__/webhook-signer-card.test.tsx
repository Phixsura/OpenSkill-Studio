import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookSignerCard from "../src/components/webhook-signer-card";

const activeSecret = {
  secret_id: "whsec_prod",
  prefix: "a1b2c3d4",
  active: true,
  created_at: new Date(Date.now() - 86_400_000).toISOString(),
};

const revokedSecret = {
  secret_id: "whsec_old",
  prefix: "e5f6g7h8",
  active: false,
  created_at: new Date(Date.now() - 86_400_000 * 30).toISOString(),
};

describe("WebhookSignerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <WebhookSignerCard secrets={[activeSecret]} appName="My App" toleranceSeconds={300} />,
    );
    expect(container.textContent).toContain("Webhook Signing");
    expect(container.textContent).toContain("My App");
  });

  it("shows algorithm badge", () => {
    const { container } = render(
      <WebhookSignerCard secrets={[activeSecret]} appName="App" toleranceSeconds={300} />,
    );
    expect(container.textContent).toContain("HMAC-SHA256");
  });

  it("shows tolerance window", () => {
    const { container } = render(
      <WebhookSignerCard secrets={[activeSecret]} appName="App" toleranceSeconds={300} />,
    );
    expect(container.textContent).toContain("300s window");
  });

  it("renders secret id and prefix", () => {
    const { container } = render(
      <WebhookSignerCard secrets={[activeSecret]} appName="App" toleranceSeconds={300} />,
    );
    expect(container.textContent).toContain("whsec_prod");
    expect(container.textContent).toContain("a1b2c3d4");
  });

  it("shows revoked label", () => {
    const { container } = render(
      <WebhookSignerCard secrets={[revokedSecret]} appName="App" toleranceSeconds={300} />,
    );
    expect(container.textContent).toContain("revoked");
  });

  it("shows active secret count", () => {
    const { container } = render(
      <WebhookSignerCard
        secrets={[activeSecret, revokedSecret]}
        appName="App"
        toleranceSeconds={300}
      />,
    );
    expect(container.textContent).toContain("1 active secret");
  });

  it("shows created time", () => {
    const { container } = render(
      <WebhookSignerCard secrets={[activeSecret]} appName="App" toleranceSeconds={300} />,
    );
    expect(container.textContent).toContain("Created");
  });

  it("shows empty state", () => {
    const { container } = render(
      <WebhookSignerCard secrets={[]} appName="App" toleranceSeconds={300} />,
    );
    expect(container.textContent).toContain("No signing secrets");
  });
});
