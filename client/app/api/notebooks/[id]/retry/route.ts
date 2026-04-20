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
        sources: true,
      },
    });

    if (!notebook) {
      return NextResponse.json(
        { error: "Notebook not found" },
        { status: 404 }
      );
    }

    // Update notebook status to IN_QUEUE
    await prisma.notebookProcessingStatus.update({
      where: {
        notebookId: id,
      },
      data: {
        status: "IN_QUEUE",
        message: "Notebook queued for reprocessing",
      },
    });

    // Call the research API
    const researchApiUrl = process.env.BACKEND_API_URL;
    if (!researchApiUrl) {
      throw new Error("BACKEND_API_URL not configured");
    }

    const sourcesToSend = notebook.sources.map((source) => ({
      source_type: source.sourceType,
      source_url: source.sourceUrl || null,
      source_content: source.content || null,
    }));

    const researchApiResponse = await fetch(`${researchApiUrl}/api/research`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({
        topic: notebook.topic || null,
        sources: sourcesToSend,
        notebook_id: notebook.id,
      }),
    });

    if (!researchApiResponse.ok) {
      throw new Error(`Research API call failed with status: ${researchApiResponse.status}`);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Error retrying notebook processing:", error);
    return NextResponse.json(
      { error: "Failed to retry notebook processing" },
      { status: 500 }
    );
  }
}