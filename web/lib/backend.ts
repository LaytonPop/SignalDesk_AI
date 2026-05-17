import { NextResponse } from "next/server";

const DEFAULT_API_BASE = "http://127.0.0.1:8000";

function apiBaseUrl() {
  return process.env.INTEL_API_BASE_URL ?? DEFAULT_API_BASE;
}

export async function proxyToBackend(path: string, init?: RequestInit) {
  try {
    const response = await fetch(`${apiBaseUrl()}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
    });

    const text = await response.text();
    const contentType = response.headers.get("content-type") ?? "application/json";

    return new NextResponse(text, {
      status: response.status,
      headers: {
        "Content-Type": contentType,
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Unable to reach backend service.",
      },
      { status: 502 },
    );
  }
}
