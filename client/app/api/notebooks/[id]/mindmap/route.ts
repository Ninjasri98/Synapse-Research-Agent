import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    // Verify the notebook exists and belongs to the user
    const notebook = await prisma.notebook.findUnique({
      where: {
        id,
        userId: session.user.id,
      },
      include: {
        output: true,
      },
    });

    if (!notebook) {
      return NextResponse.json(
        { error: "Notebook not found" },
        { status: 404 }
      );
    }

    // Check if notebook has been processed
    if (!notebook.output) {
      return NextResponse.json(
        { error: "Notebook must be processed before generating mindmap" },
        { status: 400 }
      );
    }

    // Update mindmap status to IN_PROGRESS
    await prisma.notebookOutput.update({
      where: {
        notebookId: id,
      },
      data: {
        mindmap: "IN_PROGRESS",
      },
    });

    // Call the backend mindmap API
    const backendApiUrl = process.env.BACKEND_API_URL;
    if (!backendApiUrl) {
      throw new Error("BACKEND_API_URL not configured");
    }

    const mindmapApiResponse = await fetch(`${backendApiUrl}/api/research/mindmap/${id}`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
    });

    if (!mindmapApiResponse.ok) {
      // Update mindmap status to ERROR if backend call fails
      await prisma.notebookOutput.update({
        where: {
          notebookId: id,
        },
        data: {
          mindmap: "ERROR",
        },
      });

      throw new Error(`Backend API error: ${mindmapApiResponse.status}`);
    }

    return NextResponse.json({
      status: "success",
      message: "Mindmap generation started"
    });

  } catch (error) {
    console.error("Error generating mindmap:", error);

    // Try to update mindmap status to ERROR
    try {
      const { id } = await params;
      await prisma.notebookOutput.update({
        where: {
          notebookId: id,
        },
        data: {
          mindmap: "ERROR",
        },
      });
    } catch (updateError) {
      console.error("Error updating mindmap status to ERROR:", updateError);
    }

    return NextResponse.json(
      {
        error: "Failed to generate mindmap",
        details: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    );
  }
}