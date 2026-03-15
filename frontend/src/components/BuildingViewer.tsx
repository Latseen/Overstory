'use client';

import { useEffect, useRef } from 'react';
import { drawBuilding3d } from '@/lib/building3d';
import type { Building } from '@/lib/api';

interface Props {
  building: Building;
  score: number;
}

export default function BuildingViewer({ building, score }: Props) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const scene = drawBuilding3d(canvas, { building, score });
    return () => scene.cleanup();
  }, [building, score]);

  return (
    <canvas
      ref={ref}
      style={{ width: '100%', height: '300px', display: 'block' }}
      className="max-w-sm"
    />
  );
}
