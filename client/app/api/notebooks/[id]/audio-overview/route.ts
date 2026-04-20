import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    // Get the authenticated session
    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Verify the notebook belongs to the user
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
      return NextResponse.json({ error: "Notebook not found" }, { status: 404 });
    }

    if (!notebook.output) {
      return NextResponse.json(
        { error: "Notebook must be processed before generating audio overview" },
        { status: 400 }
      );
    }

    // Update the audio overview URL to IN_PROGRESS to indicate processing
    await prisma.notebookOutput.update({
      where: {
        id: notebook.output.id,
      },
      data: {
        audioOverviewUrl: "IN_PROGRESS",
      },
    });

    // Call the backend API to generate audio overview
    const backendResponse = await fetch(
      `${process.env.BACKEND_API_URL}/api/research/audio-overview/${id}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${process.env.BACKEND_API_KEY}`,
        },
      }
    );

    if (!backendResponse.ok) {
      // Update status to ERROR if backend call fails
      await prisma.notebookOutput.update({
        where: {
          id: notebook.output.id,
        },
        data: {
          audioOverviewUrl: "ERROR",
        },
      });

      return NextResponse.json(
        { error: "Failed to generate audio overview" },
        { status: 500 }
      );
    }

    return NextResponse.json({
      message: "Audio overview generation started",
      status: "IN_PROGRESS",
    });
  } catch (error) {
    console.error("Error generating audio overview:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}