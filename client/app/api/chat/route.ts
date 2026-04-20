import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { prisma } from "@/lib/prisma";

export async function POST(request: NextRequest) {
  try {
    // Validate user session
    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session) {
      return NextResponse.json(
        { status: "error", response: "Unauthorized" },
        { status: 401 }
      );
    }

    // Get request body
    const body = await request.json();
    const { messages, notebook_id } = body;

    // Validate required fields
    if (!messages || !Array.isArray(messages) || !notebook_id) {
      return NextResponse.json(
        { status: "error", response: "Missing required fields" },
        { status: 400 }
      );
    }

    // Verify notebook belongs to the user
    try {
      const notebookCount = await prisma.notebook.count({
        where: {
          id: notebook_id,
          userId: session.user.id,
        },
      });

      if (notebookCount === 0) {
        return NextResponse.json(
          { status: "error", response: "Notebook not found or unauthorized" },
          { status: 403 }
        );
      }
    } catch (error) {
      console.error("Error verifying notebook ownership:", error);
      return NextResponse.json(
        { status: "error", response: "Error verifying notebook ownership" },
        { status: 500 }
      );
    }

    // Forward request to the backend API
    const backendApiUrl = process.env.BACKEND_API_URL;
    if (!backendApiUrl) {
      return NextResponse.json(
        { status: "error", response: "Backend API URL not configured" },
        { status: 500 }
      );
    }

    try {
      const apiResponse = await fetch(`${backendApiUrl}/api/chat/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages,
          notebook_id,
        }),
      });

      if (!apiResponse.ok) {
        const errorText = await apiResponse.text();
        throw new Error(`Backend API error: ${apiResponse.status} - ${errorText}`);
      }

      const responseData = await apiResponse.json();
      return NextResponse.json(responseData);
    } catch (error) {
      console.error("Error calling backend chat API:", error);
      return NextResponse.json(
        {
          status: "error",
          response: error instanceof Error ? error.message : "Unknown error calling backend API"
        },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error("Error processing chat request:", error);
    return NextResponse.json(
      { status: "error", response: "Internal server error" },
      { status: 500 }
    );
  }
}