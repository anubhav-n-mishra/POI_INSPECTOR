'use client';

import { ArrowLeft, Download, TrendingUp, AlertCircle, CheckCircle2, Activity, MapPin } from 'lucide-react';
import MetricsCard from './MetricsCard';
import SuggestionsPanel from './SuggestionsPanel';
import QualityGauge from './QualityGauge';

interface AnalysisViewProps {
    data: any;
    onBack: () => void;
}

export default function AnalysisView({ data, onBack }: AnalysisViewProps) {
    const handleDownloadReport = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/report/${data.analysis_id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                alert(`Report generated successfully!\n\nPath: ${result.report_path}`);
            } else {
                throw new Error('Report generation failed');
            }
        } catch (error) {
            console.error('Report error:', error);
            alert('Backend offline. Report generation requires the API server.');
        }
    };

    const getStatusBadge = () => {
        const score = data.quality_score;
        if (score >= 85) return 'badge-success';
        if (score >= 70) return 'badge-success';
        if (score >= 50) return 'badge-warning';
        return 'badge-error';
    };

    return (
        <div style={{ minHeight: '100vh', background: 'var(--surface-variant)' }}>
            {/* Header */}
            <header style={{ background: 'var(--surface)', borderBottom: '1px solid var(--outline)' }}>
                <div className="container" style={{ padding: '20px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                        <button onClick={onBack} className="material-button material-button-text">
                            <ArrowLeft size={20} />
                            <span>Back</span>
                        </button>
                        <div style={{ width: '1px', height: '24px', background: 'var(--outline)' }}></div>
                        <div>
                            <h1 className="title-large" style={{ margin: 0 }}>Analysis Report</h1>
                            <p className="body-medium" style={{ margin: 0, color: 'var(--on-surface-variant)' }}>POI ID: {data.poi_id}</p>
                        </div>
                    </div>
                    <button onClick={handleDownloadReport} className="material-button material-button-filled">
                        <Download size={20} />
                        <span>Download Report</span>
                    </button>
                </div>
            </header>

            <main className="container" style={{ paddingTop: '32px', paddingBottom: '64px' }}>
                {/* Quality Score Section */}
                <div className="material-card elevation-2" style={{ marginBottom: '24px', padding: '32px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '48px', alignItems: 'center' }}>
                        {/* Gauge */}
                        <div style={{ textAlign: 'center' }}>
                            <QualityGauge score={data.quality_score} />
                            <div style={{ marginTop: '24px' }}>
                                <div className="display-small" style={{ color: 'var(--google-blue)', marginBottom: '8px' }}>
                                    {data.quality_score}
                                </div>
                                <p className="body-large" style={{ color: 'var(--on-surface-variant)', margin: 0 }}>out of 100</p>
                                <div style={{ marginTop: '16px' }}>
                                    <span className={`material-badge ${getStatusBadge()}`}>
                                        {data.quality_status.emoji} {data.quality_status.status} · Grade {data.quality_grade}
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Status */}
                        <div>
                            <h2 className="headline-medium" style={{ marginBottom: '16px' }}>Overall Quality</h2>
                            <p className="body-large" style={{ color: 'var(--on-surface-variant)', marginBottom: '24px' }}>
                                {data.quality_status.description}
                            </p>
                            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                                <div className="material-chip">
                                    <CheckCircle2 size={16} />
                                    <span suppressHydrationWarning>Analyzed: {new Date(data.timestamp).toLocaleString()}</span>
                                </div>
                                <div className="material-chip">
                                    <Activity size={16} />
                                    <span>ID: {data.analysis_id.slice(0, 12)}...</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Metrics Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                    <MetricsCard
                        label="IOU Score"
                        value={`${(data.metrics.iou * 100).toFixed(1)}%`}
                        description="Intersection over Union"
                        status={data.metrics.iou >= 0.7 ? 'good' : data.metrics.iou >= 0.5 ? 'fair' : 'poor'}
                        icon={<TrendingUp size={20} />}
                    />

                    <MetricsCard
                        label="Leakage"
                        value={`${data.metrics.leakage_percentage.toFixed(1)}%`}
                        description="Area outside building"
                        status={data.metrics.leakage_percentage <= 10 ? 'good' : data.metrics.leakage_percentage <= 25 ? 'fair' : 'poor'}
                        icon={<AlertCircle size={20} />}
                    />

                    <MetricsCard
                        label="Coverage"
                        value={`${data.metrics.coverage_percentage.toFixed(1)}%`}
                        description="Building coverage"
                        status={data.metrics.coverage_percentage >= 80 ? 'good' : data.metrics.coverage_percentage >= 60 ? 'fair' : 'poor'}
                        icon={<CheckCircle2 size={20} />}
                    />

                    <MetricsCard
                        label="Regularity"
                        value={`${data.metrics.regularity_score.toFixed(1)}/100`}
                        description="Shape regularity"
                        status={data.metrics.regularity_score >= 60 ? 'good' : data.metrics.regularity_score >= 40 ? 'fair' : 'poor'}
                        icon={<Activity size={20} />}
                    />

                    <MetricsCard
                        label="Road Overlap"
                        value={`${data.metrics.road_overlap_percentage.toFixed(1)}%`}
                        description="Overlapping roads"
                        status={data.metrics.road_overlap_percentage <= 10 ? 'good' : data.metrics.road_overlap_percentage <= 25 ? 'fair' : 'poor'}
                        icon={<AlertCircle size={20} />}
                    />

                    <MetricsCard
                        label="Adjacent POIs"
                        value={data.metrics.adjacent_overlap.overlap_count.toString()}
                        description="Overlapping POIs"
                        status={data.metrics.adjacent_overlap.overlap_count === 0 ? 'good' : 'fair'}
                        icon={<MapPin size={20} />}
                    />
                </div>

                {/* Suggestions and Map */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
                    <SuggestionsPanel suggestions={data.suggestions} />

                    {/* Satellite Map View */}
                    <div className="material-card elevation-1">
                        <h3 className="title-medium" style={{ marginBottom: '16px' }}>Satellite View</h3>
                        <div style={{ aspectRatio: '1', background: 'var(--surface-variant)', borderRadius: '8px', overflow: 'hidden', position: 'relative' }}>
                            <img
                                src={`http://localhost:8000/api/satellite/${data.poi_id}`}
                                alt="Satellite View"
                                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                onError={(e) => {
                                    e.currentTarget.style.display = 'none';
                                    e.currentTarget.parentElement!.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--on-surface-variant)">Satellite image unavailable</div>';
                                }}
                            />
                            <div style={{ position: 'absolute', bottom: '12px', right: '12px', background: 'rgba(0,0,0,0.6)', color: 'white', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
                                ESRI World Imagery
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
