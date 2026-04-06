'use client';

import { useEffect, useRef } from 'react';

interface QualityGaugeProps {
    score: number;
}

export default function QualityGauge({ score }: QualityGaugeProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 90;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Background arc
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0.75 * Math.PI, 2.25 * Math.PI);
        ctx.lineWidth = 20;
        ctx.strokeStyle = '#dadce0';
        ctx.stroke();

        // Score arc with Google colors
        const scoreAngle = 0.75 * Math.PI + (score / 100) * 1.5 * Math.PI;

        let color;
        if (score >= 85) color = '#34a853'; // Google Green
        else if (score >= 70) color = '#1a73e8'; // Google Blue
        else if (score >= 50) color = '#fbbc04'; // Google Yellow
        else color = '#ea4335'; // Google Red

        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0.75 * Math.PI, scoreAngle);
        ctx.lineWidth = 20;
        ctx.strokeStyle = color;
        ctx.lineCap = 'round';
        ctx.stroke();

        // Center circle
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius - 30, 0, 2 * Math.PI);
        ctx.fillStyle = '#ffffff';
        ctx.fill();

    }, [score]);

    return (
        <div style={{ width: '220px', height: '220px', margin: '0 auto' }}>
            <canvas
                ref={canvasRef}
                width={220}
                height={220}
                style={{ display: 'block' }}
            />
        </div>
    );
}
