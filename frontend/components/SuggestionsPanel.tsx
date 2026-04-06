'use client';

import { Lightbulb } from 'lucide-react';

interface SuggestionsPanelProps {
    suggestions: string[];
}

export default function SuggestionsPanel({ suggestions }: SuggestionsPanelProps) {
    return (
        <div className="material-card elevation-1">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <div style={{ width: '40px', height: '40px', background: 'rgba(251, 188, 4, 0.1)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Lightbulb size={20} color="var(--google-yellow)" />
                </div>
                <h3 className="title-medium" style={{ margin: 0 }}>Improvement Suggestions</h3>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {suggestions.map((suggestion, index) => (
                    <div
                        key={index}
                        style={{
                            padding: '16px',
                            background: 'var(--surface-variant)',
                            borderRadius: '8px',
                            borderLeft: '3px solid var(--google-blue)'
                        }}
                    >
                        <p className="body-medium" style={{ margin: 0, color: 'var(--on-surface)' }}>{suggestion}</p>
                    </div>
                ))}
            </div>

            {suggestions.length === 0 && (
                <div style={{ textAlign: 'center', padding: '48px 24px' }}>
                    <Lightbulb size={48} color="var(--on-surface-variant)" style={{ opacity: 0.3, marginBottom: '16px' }} />
                    <p className="body-medium" style={{ color: 'var(--on-surface-variant)' }}>No suggestions - POI quality is excellent!</p>
                </div>
            )}
        </div>
    );
}
