'use client';

import { useState, useRef } from 'react';
import { Upload, Activity, TrendingUp, Shield, CheckCircle2, FileJson, Sparkles } from 'lucide-react';
import AnalysisView from '@/components/AnalysisView';

export default function Home() {
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsAnalyzing(true);
    setError('');

    try {
      const text = await file.text();
      const geojson = JSON.parse(text);
      const feature = geojson.features?.[0];

      if (!feature) {
        throw new Error('No POI found in GeoJSON file');
      }

      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          poi_id: feature.properties?.id || `poi_${Date.now()}`,
          polygon: feature.geometry,
          metadata: feature.properties || {}
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      setAnalysisData(data);
    } catch (err: any) {
      setError(err.message || 'Analysis failed');
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDemoAnalysis = async () => {
    setIsAnalyzing(true);
    setError('');

    try {
      // Sample polygon (Googleplex) for demo
      const samplePolygon = {
        "type": "Polygon",
        "coordinates": [
          [
            [-122.0842, 37.4220],
            [-122.0837, 37.4220],
            [-122.0837, 37.4215],
            [-122.0842, 37.4215],
            [-122.0842, 37.4220]
          ]
        ]
      };

      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          poi_id: `demo_${Date.now()}`,
          polygon: samplePolygon,
          metadata: { name: "Demo POI (Googleplex)" }
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      setAnalysisData(data);
    } catch (err: any) {
      setError(err.message || 'Demo analysis failed');
      console.error('Demo error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  if (analysisData) {
    return <AnalysisView data={analysisData} onBack={() => setAnalysisData(null)} />;
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--surface-variant)' }}>
      {/* Header */}
      <header style={{ background: 'var(--surface)', borderBottom: '1px solid var(--outline)' }}>
        <div className="container" style={{ padding: '20px 24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ width: '40px', height: '40px', background: 'var(--google-blue)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Activity size={24} color="white" />
          </div>
          <div>
            <h1 className="title-large" style={{ margin: 0 }}>POI Quality Inspector</h1>
            <p className="body-medium" style={{ margin: 0, color: 'var(--on-surface-variant)' }}>Powered by AI</p>
          </div>
        </div>
      </header>

      <main className="container" style={{ paddingTop: '64px', paddingBottom: '64px' }}>
        {/* Hero Section */}
        <div className="fade-in" style={{ textAlign: 'center', marginBottom: '64px', maxWidth: '800px', margin: '0 auto 64px' }}>
          <div className="material-chip" style={{ marginBottom: '24px' }}>
            <Sparkles size={16} />
            <span>AI-Powered Geospatial Analysis</span>
          </div>

          <h2 className="display-small" style={{ marginBottom: '24px', color: 'var(--on-surface)' }}>
            Verify Point-of-Interest polygon accuracy with precision
          </h2>

          <p className="body-large" style={{ color: 'var(--on-surface-variant)', marginBottom: '40px' }}>
            Analyze POI boundaries using satellite imagery and computer vision. Get instant quality scores and actionable recommendations to improve location data accuracy.
          </p>
        </div>

        {/* Upload Card */}
        <div className="material-card elevation-2 fade-in" style={{ maxWidth: '600px', margin: '0 auto 48px', animation: 'fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.2s both' }}>
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <div style={{ width: '80px', height: '80px', margin: '0 auto 24px', background: 'rgba(26, 115, 232, 0.08)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FileJson size={40} color="var(--google-blue)" />
            </div>
            <h3 className="headline-small" style={{ marginBottom: '8px' }}>Upload POI Data</h3>
            <p className="body-medium" style={{ color: 'var(--on-surface-variant)' }}>GeoJSON format with polygon geometries required</p>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept=".geojson,.json"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
            disabled={isAnalyzing}
          />

          <button
            onClick={handleUploadClick}
            className="material-button material-button-outlined"
            style={{ width: '100%', justifyContent: 'center', padding: '16px 24px', marginBottom: '16px' }}
            disabled={isAnalyzing}
          >
            <Upload size={20} />
            <span>{isAnalyzing ? 'Analyzing...' : 'Choose GeoJSON File'}</span>
          </button>

          <div className="material-divider" style={{ margin: '24px 0' }}></div>

          <button
            onClick={handleDemoAnalysis}
            className="material-button material-button-filled"
            style={{ width: '100%', justifyContent: 'center', padding: '16px 24px' }}
            disabled={isAnalyzing}
          >
            <Activity size={20} />
            <span>Run Demo Analysis</span>
          </button>

          {error && (
            <div className="material-card" style={{ marginTop: '16px', background: 'rgba(234, 67, 53, 0.08)', border: '1px solid rgba(234, 67, 53, 0.2)', padding: '16px' }}>
              <p className="body-medium" style={{ color: 'var(--google-red)', margin: 0 }}>{error}</p>
            </div>
          )}

          {isAnalyzing && (
            <div style={{ marginTop: '32px', textAlign: 'center' }}>
              <div className="material-spinner" style={{ margin: '0 auto 16px' }}></div>
              <p className="body-medium" style={{ color: 'var(--on-surface-variant)' }}>Analyzing POI quality metrics...</p>
            </div>
          )}
        </div>

        {/* Features Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px', marginBottom: '64px' }}>
          {[
            {
              icon: <Shield size={24} color="var(--google-blue)" />,
              title: 'Building Detection',
              description: 'AI-powered footprint extraction using pretrained computer vision models for precise boundary identification'
            },
            {
              icon: <TrendingUp size={24} color="var(--google-green)" />,
              title: 'Quality Scoring',
              description: 'Comprehensive 0-100 metric based on IOU, leakage, coverage, and geometric regularity analysis'
            },
            {
              icon: <CheckCircle2 size={24} color="var(--google-yellow)" />,
              title: 'Smart Corrections',
              description: 'Actionable recommendations with directional guidance to optimize polygon accuracy and precision'
            }
          ].map((feature, index) => (
            <div key={index} className="material-card elevation-1 fade-in" style={{ animation: `fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) ${0.4 + index * 0.1}s both` }}>
              <div style={{ width: '48px', height: '48px', marginBottom: '16px', background: 'rgba(26, 115, 232, 0.08)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {feature.icon}
              </div>
              <h4 className="title-medium" style={{ marginBottom: '8px' }}>{feature.title}</h4>
              <p className="body-medium" style={{ color: 'var(--on-surface-variant)', margin: 0 }}>{feature.description}</p>
            </div>
          ))}
        </div>

        {/* How It Works */}
        <div className="material-card elevation-2" style={{ padding: '48px' }}>
          <h3 className="headline-medium" style={{ textAlign: 'center', marginBottom: '48px' }}>How It Works</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '32px' }}>
            {[
              { step: '1', title: 'Upload', desc: 'Provide GeoJSON with POI polygons' },
              { step: '2', title: 'Analyze', desc: 'AI processes satellite imagery' },
              { step: '3', title: 'Score', desc: 'Get comprehensive quality metrics' },
              { step: '4', title: 'Improve', desc: 'Apply suggested corrections' }
            ].map((item) => (
              <div key={item.step} style={{ textAlign: 'center' }}>
                <div style={{ width: '56px', height: '56px', margin: '0 auto 16px', background: 'var(--google-blue)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '24px', fontWeight: 700 }}>
                  {item.step}
                </div>
                <h5 className="title-medium" style={{ marginBottom: '8px' }}>{item.title}</h5>
                <p className="body-medium" style={{ color: 'var(--on-surface-variant)', margin: 0 }}>{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer style={{ background: 'var(--surface)', borderTop: '1px solid var(--outline)', marginTop: '64px' }}>
        <div className="container" style={{ padding: '32px 24px', textAlign: 'center' }}>
          <p className="body-medium" style={{ color: 'var(--on-surface-variant)', margin: 0 }}>
            POI Quality Inspector · Built for GroundTruth Internship Application
          </p>
          <p className="body-medium" style={{ color: 'var(--on-surface-variant)', margin: '8px 0 0 0' }}>
            Made by Anubhav Mishra ·{' '}
            <a
              href="https://github.com/anubhav-n-mishra"
              target="_blank"
              rel="noreferrer"
              style={{ color: 'var(--google-blue)', textDecoration: 'none' }}
            >
              GitHub
            </a>
            {' '}·{' '}
            <a
              href="https://linkedin.com/in/anubhav-mishra0"
              target="_blank"
              rel="noreferrer"
              style={{ color: 'var(--google-blue)', textDecoration: 'none' }}
            >
              Portfolio
            </a>
            {' '}·{' '}
            <a
              href="https://mishraanubhav.me"
              target="_blank"
              rel="noreferrer"
              style={{ color: 'var(--google-blue)', textDecoration: 'none' }}
            >
              Website
            </a>
          </p>
        </div>
      </footer>

      <a
        href="https://mishraanubhav.me"
        target="_blank"
        rel="noreferrer"
        style={{
          position: 'fixed',
          right: '16px',
          bottom: '16px',
          zIndex: 1000,
          background: 'rgba(255, 255, 255, 0.96)',
          border: '1px solid var(--outline)',
          borderRadius: '999px',
          padding: '8px 12px',
          fontSize: '12px',
          fontWeight: 600,
          color: 'var(--google-blue)',
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.12)',
          textDecoration: 'none'
        }}
        aria-label="Made by Anubhav Mishra"
      >
        Made by Anubhav Mishra · mishraanubhav.me
      </a>
    </div>
  );
}
