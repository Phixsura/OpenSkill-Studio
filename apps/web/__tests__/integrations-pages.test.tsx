import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/orgs/ORG/integrations",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useParams: () => ({ orgId: "ORG1234567890123456789012" }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {
    constructor(
      public status: number,
      public code: string,
      message: string,
    ) {
      super(message);
    }
  },
}));

import IntegrationsHubPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/integrations/page";
import DataPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/integrations/data/page";
import EventsPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/integrations/events/page";
import IdentityPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/integrations/identity/page";
import SyncPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/integrations/sync/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

beforeEach(() => {
  vi.clearAllMocks();
});

function route(table: Record<string, unknown>) {
  api.mockImplementation((path: string) => {
    for (const [prefix, payload] of Object.entries(table)) {
      if (path.startsWith(prefix)) return Promise.resolve(payload);
    }
    return Promise.resolve({ data: [] });
  });
}

describe("integrations hub", () => {
  it("renders connections with health badges and pings", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/providers": {
        data: [
          {
            id: "p1",
            key: "oneroster",
            category: "roster",
            auth_mode: "oauth2_cc",
            display_name: "OneRoster 1.2 (SIS)",
            config_schema: {},
          },
        ],
      },
      "/orgs/ORG1234567890123456789012/integrations/connections/c1/ping": {
        data: { ok: true, status: "active" },
      },
      "/orgs/ORG1234567890123456789012/integrations/connections": {
        data: [
          {
            id: "c1",
            provider_key: "oneroster",
            name: "District SIS",
            status: "degraded",
            base_url: "https://sis.example.com",
            health: { last_error_class: "CONNECTION_PING_FAILED" },
            has_credential: false,
          },
        ],
      },
    });
    render(<IntegrationsHubPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText("District SIS")).toBeTruthy());
    expect(screen.getByText("degraded")).toBeTruthy();
    expect(screen.getByText("no credential")).toBeTruthy();
    expect(screen.getByText("CONNECTION_PING_FAILED")).toBeTruthy();
    fireEvent.click(screen.getByText("Ping"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/connections/c1/ping",
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });

  it("creates a connection from the catalog", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/providers": {
        data: [
          {
            id: "p1",
            key: "generic_rest",
            category: "generic",
            auth_mode: "api_key",
            display_name: "Generic REST API",
            config_schema: {},
          },
        ],
      },
    });
    render(<IntegrationsHubPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText(/Generic REST API/)).toBeTruthy());
    fireEvent.change(screen.getByLabelText("Provider"), {
      target: { value: "generic_rest" },
    });
    fireEvent.change(screen.getByLabelText("Connection name"), {
      target: { value: "CRM" },
    });
    fireEvent.click(screen.getByText("Create"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/connections",
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });
});

describe("events page", () => {
  it("lists deliveries, expands attempts and replays", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/deliveries/d1/replay": { data: {} },
      "/orgs/ORG1234567890123456789012/integrations/deliveries/d1": {
        data: {
          id: "d1",
          event_id: "e1",
          event_type: "com.openskill.project.approved.v1",
          subscription_id: "s1",
          status: "exhausted",
          attempt_count: 8,
          next_attempt_at: null,
          replay_of: null,
          attempts: [
            {
              id: "a1",
              status_code: 500,
              error: "http_500",
              latency_ms: 42,
              attempted_at: "2026-10-11T01:00:00Z",
            },
          ],
        },
      },
      "/orgs/ORG1234567890123456789012/integrations/deliveries": {
        data: [
          {
            id: "d1",
            event_id: "e1",
            event_type: "com.openskill.project.approved.v1",
            subscription_id: "s1",
            status: "exhausted",
            attempt_count: 8,
            next_attempt_at: null,
            replay_of: null,
          },
        ],
      },
      "/orgs/ORG1234567890123456789012/integrations/events": {
        data: [
          {
            id: "e1",
            type: "com.openskill.project.approved.v1",
            subject: "sub-1",
            time: "2026-10-11T00:00:00Z",
          },
        ],
      },
    });
    render(<EventsPage />, { wrapper: wrapper() });
    // NOTE: "exhausted" also exists as a static <option> — wait on a
    // data-only marker instead so the list has actually rendered.
    await waitFor(() => expect(screen.getByText("attempts: 8")).toBeTruthy());
    fireEvent.click(screen.getByText("Attempts"));
    await waitFor(() => expect(screen.getByText(/http_500/)).toBeTruthy());
    fireEvent.click(screen.getByText("Replay"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/deliveries/d1/replay",
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });

  it("manages subscriptions: create reveals secret once, rotate re-reveals", async () => {
    route({
      "/orgs/ORG1234567890123456789012/webhooks/w1/rotate-secret": {
        data: {
          id: "w1",
          url: "https://r.example.com/h",
          events: ["project.approved"],
          secret: "whsec_ROTATED",
          active: true,
        },
      },
      "/orgs/ORG1234567890123456789012/webhooks": {
        data: [
          {
            id: "w1",
            url: "https://r.example.com/h",
            events: ["project.approved"],
            secret: "whse****TED",
            active: true,
          },
        ],
      },
    });
    render(<EventsPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText("https://r.example.com/h")).toBeTruthy());
    fireEvent.click(screen.getByText("Rotate secret"));
    await waitFor(() => expect(screen.getByText(/whsec_ROTATED/)).toBeTruthy());
    expect(api).toHaveBeenCalledWith(
      "/orgs/ORG1234567890123456789012/webhooks/w1/rotate-secret?immediate=false",
      expect.objectContaining({ method: "POST" }),
    );

    // Create path: POST then the once-only secret banner swaps to the new one.
    api.mockImplementationOnce(() =>
      Promise.resolve({
        data: {
          id: "w2",
          url: "https://r2.example.com/h",
          events: ["com.openskill.integration.*"],
          secret: "whsec_NEW2",
          active: true,
        },
      }),
    );
    fireEvent.change(screen.getByLabelText("Webhook URL"), {
      target: { value: "https://r2.example.com/h" },
    });
    fireEvent.change(screen.getByLabelText("Event patterns"), {
      target: { value: "com.openskill.integration.*" },
    });
    fireEvent.click(screen.getByText("Subscribe"));
    await waitFor(() => expect(screen.getByText(/whsec_NEW2/)).toBeTruthy());
  });
});

describe("identity page", () => {
  it("shows TXT instructions for pending domains and mints SCIM tokens once", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/domains": {
        data: [
          {
            id: "dm1",
            domain: "school.example.edu",
            status: "pending",
            verification_token: "osks-verify-abc",
          },
        ],
      },
      "/orgs/ORG1234567890123456789012/integrations/sso-connections": { data: [] },
      "/orgs/ORG1234567890123456789012/integrations/scim-tokens": { data: [] },
      "/orgs/ORG1234567890123456789012/integrations/identity-queue": {
        data: [
          {
            id: "q1",
            source: "sso",
            subject: "sub-9",
            email: "x@school.example.edu",
            reason: "no_member_match",
            status: "pending",
          },
        ],
      },
    });
    render(<IdentityPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText(/osks-verify-abc/)).toBeTruthy());
    // mint a token: the raw value must surface exactly once
    api.mockResolvedValueOnce({
      data: {
        id: "t1",
        name: "Entra",
        token: "osks_scim_RAW",
        last_used_at: null,
        revoked_at: null,
      },
    });
    fireEvent.change(screen.getByLabelText("Token name"), { target: { value: "Entra" } });
    fireEvent.click(screen.getByText("Mint token"));
    await waitFor(() => expect(screen.getByText(/osks_scim_RAW/)).toBeTruthy());
    // queue item renders with reject action
    expect(screen.getByText(/no_member_match/)).toBeTruthy();
    fireEvent.click(screen.getByText("Reject"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/identity-queue/q1/resolve",
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });
});

describe("sync page", () => {
  it("runs profiles and surfaces conflicts", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/sync-profiles/sp1/run": { data: {} },
      "/orgs/ORG1234567890123456789012/integrations/sync-profiles": {
        data: [
          {
            id: "sp1",
            connection_id: "c1",
            name: "roster",
            model: "roster.class",
            direction: "pull",
            schedule: "manual",
            enabled: true,
          },
        ],
      },
      "/orgs/ORG1234567890123456789012/integrations/sync-runs/r1/records": {
        data: [
          {
            id: "rr1",
            external_id: "e-9",
            model: "roster.enrollment",
            outcome: "conflict",
            conflict_class: "ambiguous_identity",
            detail: {},
          },
        ],
      },
      "/orgs/ORG1234567890123456789012/integrations/sync-runs": {
        data: [
          {
            id: "r1",
            profile_id: "sp1",
            status: "partial",
            trigger: "manual",
            stats: { read: 5, conflicts: 1 },
            error: null,
            started_at: null,
            finished_at: null,
          },
        ],
      },
    });
    render(<SyncPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText("roster")).toBeTruthy());
    fireEvent.click(screen.getByText("Run"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/sync-profiles/sp1/run?backfill=false",
        expect.objectContaining({ method: "POST" }),
      ),
    );
    fireEvent.click(screen.getByText("Conflicts"));
    await waitFor(() => expect(screen.getByText(/ambiguous_identity/)).toBeTruthy());
  });
});

describe("data page", () => {
  it("creates export streams and runs them", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/export-streams/es1/run": {
        data: { id: "er1", status: "succeeded", row_count: 3, manifest_key: "m", created_at: "" },
      },
      "/orgs/ORG1234567890123456789012/integrations/export-streams": {
        data: [
          {
            id: "es1",
            name: "nightly",
            dataset: "events",
            field_allowlist: ["id", "type"],
            schedule: "manual",
            cursor: {},
          },
        ],
      },
    });
    render(<DataPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText("nightly")).toBeTruthy());
    fireEvent.click(screen.getByText("Run export"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/export-streams/es1/run",
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });
});
